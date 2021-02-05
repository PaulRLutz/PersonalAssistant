from base_classes.Plugin import Plugin
import datetime
import json
import urllib.request
import urllib
import collections
import os
import traceback
from helpers import network_helpers

WeatherData = collections.namedtuple('WeatherData', 'timestamp, data')

ASTRONOMY_KEY = "astronomy"
FORECAST10DAY_KEY = "forecast10day"
HOURLY10DAY_KEY = "hourly10day"
CONDITIONS_KEY = "conditions"

STATUS_SUNSET_KEY = "sunset"
STATUS_FORECAST_KEY = "forecast_text"
STATUS_FORECAST_NIGHT_KEY = "night_forecast_text"
STATUS_TEN_DAY_FORECAST_KEY = "ten_day_forecast"
STATUS_CURRENT_CONDITIONS_KEY = "current_conditions"

ERROR_WEATHER_DATA_NETWORK = "there was a network error getting the weather data"
ERROR_WEATHER_DATA_GENERIC = "there was an error getting the weather data"

class WeatherUndergroundPlugin(Plugin):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.ZIP_CODE = self.assistant.weather_underground_config_dict["location"]["zip"]
    self.LAT = self.assistant.weather_underground_config_dict["location"]["latitude"]
    self.LON = self.assistant.weather_underground_config_dict["location"]["longitude"]
    self.API_KEY = self.assistant.api_keys_credentials_dict["main"]["weather_underground"]

    self.weather_urls = {
        ASTRONOMY_KEY : f"http://api.wunderground.com/api/{self.API_KEY}/astronomy/q/{self.LAT},{self.LON}.json",
        FORECAST10DAY_KEY : f"http://api.wunderground.com/api/{self.API_KEY}/forecast10day/q/{self.LAT},{self.LON}.json",
        HOURLY10DAY_KEY : f"http://api.wunderground.com/api/{self.API_KEY}/hourly10day/q/{self.LAT},{self.LON}.json",
        CONDITIONS_KEY : f"http://api.wunderground.com/api/{self.API_KEY}/conditions/q/{self.LAT},{self.LON}.json",
        }
    self.weather_data = {}

  def refresh_status(self):
    """Populates the self.status dict."""
    try:
      sunset_hour, sunset_minute = self.get_sunset_time()
      sunset_time = self.get_readable_time(datetime.datetime.strptime(f"{sunset_hour} {sunset_minute}", "%H %M").timestamp())
    except network_helpers.NoInternetException:
      self.log.error(ERROR_WEATHER_DATA_NETWORK)
      sunset_time = ERROR_WEATHER_DATA_NETWORK
    except:
      self.log.error(ERROR_WEATHER_DATA_GENERIC)
      self.log.error(traceback.format_exc())
      sunset_time = ERROR_WEATHER_DATA_GENERIC
    
    try:
      forecast, night_forecast = self.get_forecast()
      forecast = forecast["fcttext"]
      night_forecast = night_forecast["fcttext"]
    except network_helpers.NoInternetException:
      forecast = ERROR_WEATHER_DATA_NETWORK
      night_forecast = ERROR_WEATHER_DATA_NETWORK
    except:
      self.log.error(traceback.format_exc())
      forecast = ERROR_WEATHER_DATA_GENERIC
      night_forecast = ERROR_WEATHER_DATA_GENERIC

    try:
      ten_day_forecast = self.get_ten_day_forecast_list()
    except network_helpers.NoInternetException:
      ten_day_forecast = ERROR_WEATHER_DATA_NETWORK
    except:
      self.log.error(traceback.format_exc())
      ten_day_forecast = ERROR_WEATHER_DATA_GENERIC

    try:
      current_conditions = self.get_current_conditions()
      if ten_day_forecast != ERROR_WEATHER_DATA_GENERIC and ten_day_forecast != ERROR_WEATHER_DATA_NETWORK:
        current_conditions["high_temp"] = ten_day_forecast[0]["high_temp"]
        current_conditions["low_temp"] = ten_day_forecast[0]["low_temp"]
        current_conditions["average_humidity"] = ten_day_forecast[0]["average_humidity"]
    except network_helpers.NoInternetException:
      current_conditions = ERROR_WEATHER_DATA_NETWORK
    except:
      self.log.error(traceback.format_exc())
      current_conditions = ERROR_WEATHER_DATA_GENERIC

    self.status[STATUS_SUNSET_KEY] = sunset_time
    self.status[STATUS_FORECAST_KEY] = forecast
    self.status[STATUS_FORECAST_NIGHT_KEY] = night_forecast
    self.status[STATUS_TEN_DAY_FORECAST_KEY] = ten_day_forecast 
    self.status[STATUS_CURRENT_CONDITIONS_KEY] = current_conditions 

  """
    Helper functions
  """

  def get_weather(self, weather_key):
    """
      Gets weather data. First checks in memory, then cached, then pulls from internet.
      Args:
        weather_key (str): Specifies which type of weather data to get.
      Returns:
        dict: Contains weather data determined by weather_key.
      Raises:
        network_helpers.NoInternetException: If no internet connection exists.
    """
    if not network_helpers.internet_check():
      raise network_helpers.NoInternetException()

    if weather_key in self.weather_data:
      if not self.should_update_weather(self.weather_data[weather_key].timestamp):
        self.log.debug("in memory weather data is valid")
        return self.weather_data[weather_key].data

    self.log.debug("no weather data in memory, check for cached")
    cache_success, weather_data_bytes, weather_timestamp = self.get_cached_weather(weather_key)
    if cache_success:
      try:
        weather_data = json.loads(weather_data_bytes)
        self.log.debug("got weather data from cache")
      except json.decoder.JSONDecodeError:
        self.log.warn("problem getting cached weather data")
        cache_success = False

    if not cache_success or self.should_update_weather(weather_timestamp):
      self.log.debug("no or invalid cached data, fetch from online")
      weather_data_bytes = self.fetch_weather(weather_key)
      if weather_data_bytes is None:
        return None
      weather_timestamp = int(datetime.datetime.now().timestamp())

      self.update_cached_weather(weather_key, weather_timestamp, weather_data_bytes)

      weather_data = json.loads(weather_data_bytes)
      
    self.weather_data[weather_key] = WeatherData(timestamp=weather_timestamp, data=weather_data)
    return self.weather_data[weather_key].data

  def update_cached_weather(self, weather_key, weather_timestamp, weather_data_bytes):
    """Updates the cached weather data.
    Args:
      weather_key (str): Specifies which type of weather data to update.
      weather_timestamp (float): The time that the given weather data was updated.
      weather_data_bytes (bytes): The raw bytes of the weather data to be cahced.
    """
    for file_name in os.listdir(self.DATA_FOLDER()):
      if file_name.startswith("."):
        continue
      if weather_key in file_name:
        os.remove(os.path.join(self.DATA_FOLDER(), file_name))

    with open(os.path.join(self.DATA_FOLDER(), f"{weather_key}.{weather_timestamp}"), "wb") as cached_file:
      cached_file.write(weather_data_bytes)


  def get_cached_weather(self, weather_key):
    """Gets the cached weather data.
    Args:
      weather_key (str): Specified which type of cached weather data to get.
    Returns:
      bool: True if cached data exists, False otherwise.
      bytes: The weather data in bytes.
      float: The timestamp that the cached weather data was originally retreived.
    """
    for file_name in os.listdir(self.DATA_FOLDER()):
      if file_name.startswith("."):
        continue
      if weather_key in file_name:
        timestamp = int(file_name.split(".")[1])
        with open(os.path.join(self.DATA_FOLDER(), file_name), "rb") as cached_file:
          weather_data_bytes = cached_file.read()
        return True, weather_data_bytes, timestamp

    return False, None, None

  # TODO raise nointernetconnection
  def fetch_weather(self, weather_key):
    """Gets raw weather data from weather underground api.
    Args: 
      weather_key (str): Specifies which type of weather data to get.
    Returns:
      bytes: The weather data in bytes. Defaults to None if there was an error.
    """
    try:
      with urllib.request.urlopen(self.weather_urls[weather_key]) as url:
        weather_data_bytes = url.read()
    except ConnectionResetError:
      self.log.error("problem getting weather data, connection reset")
      weather_data_bytes = None
    except urllib.error.URLError:
      self.log.error("problem getting weather data, url error")
      weather_data_bytes = None 
    return weather_data_bytes

  def should_update_weather(self, timestamp):
    """Check to see if the weather should be updated based on the timestamp (3 hours ago or more).
    Args:
      timestamp (float): The timestamp that the weather data was fetched.
    Returns:
      bool: True if the timestamp was more than three hours ago. 
    """
    if timestamp is None:
      return True
    date = self.get_datetime_obj(timestamp)
    if date < datetime.datetime.now()-datetime.timedelta(hours=3): # TODO Put weather refresh interval into a config.
      return True
    return False

  def get_datetime_obj(self, timestamp):
    """Gets the properly datetime object from timestamp.
    Args:
      timestamp (float): The timestamp to convert to a datetime.
    Returns:
      datetime: The date 
    """
    return datetime.datetime.fromtimestamp(timestamp)

  def get_readable_date(self, timestamp=None, datetime_obj=None):
    """Gets the time from a datetime_obj/timestamp in a human readable string (<MONTH> <DAY_OF_MONTH>, <YEAR>)
    Args:
      timestamp (float, optional): A timestamp.
      datetime (datetime, optional): A datetime object.
    Returns:
      str: A human-readable time string (month day_of_month, year)
    """
    if timestamp is not None:
      datetime.datetime.fromtimestamp(timestamp)
    elif datetime_obj is not None:
      pass
    else:
      return None

    return datetime_obj.strftime("%B %d, %Y")

  def get_readable_time(self, timestamp=None, datetime_obj=None):
    """Gets the time from a datetime_obj/timestamp in a human readable string (<HOUR>:<MINUTE> <AM/PM>)
    Args:
      timestamp (float, optional): A timestamp.
      datetime (datetime, optional): A datetime object.
    Returns:
      str: A human-readable time string.
    """
    if timestamp is not None:
      datetime_obj = datetime.datetime.fromtimestamp(timestamp)
    elif datetime_obj is not None:
      pass
    else:
      return None

    return datetime_obj.strftime("%I:%M %p") # hr(12):minute AM/PM (ex: 07 35 PM)

  def get_sunset_time(self):
    """Gets the sunset time in hours and minutes
    Returns:
      str: Hour of the sunset.
      str: Minute of the sunset.
    """
    astronomy = self.get_weather(ASTRONOMY_KEY)

    if astronomy is None:
      return False, "there was a problem getting the weather data"
    sunset_hour = astronomy["sun_phase"]["sunset"]["hour"]
    sunset_minute = astronomy["sun_phase"]["sunset"]["minute"]
    
    return sunset_hour, sunset_minute

  def get_current_conditions(self):
    current_conditions = self.get_weather(CONDITIONS_KEY)

    current_conditions_dict = {}
    current_conditions_dict["temperature"] = current_conditions["current_observation"]["temp_f"]
    current_conditions_dict["icon"] = current_conditions["current_observation"]["icon"]

    return current_conditions_dict

  def get_ten_day_forecast_list(self):
    forecast_list = []

    forecast_data = self.get_weather(FORECAST10DAY_KEY)
    fc_list = forecast_data["forecast"]["simpleforecast"]["forecastday"]
    for forecast in fc_list:
      forecast_dict = {}
      forecast_dict["day"] = forecast["date"]["weekday_short"]
      forecast_dict["high_temp"] = forecast["high"]["fahrenheit"]
      forecast_dict["low_temp"] = forecast["low"]["fahrenheit"]
      forecast_dict["icon"] = forecast["icon"]
      forecast_dict["average_humidity"] = forecast["avehumidity"]

      forecast_list.append(forecast_dict)

    return forecast_list
  
  def get_forecast(self, day="today"):
    """Gets the forecast object.
    Args:
      day (str, optional): The day of the week to get the forecast. "today" and "tomorrow" are also acceptable.
    Returns:
      dict: For the given day, contains the forecast text (key="fcttext"), and the icon name for the forecast (key="icon")
      dict: For the given day (night), contains the forecast text (key="fcttext"), and the icon name for the forecast (key="icon")
    """
    forecast_data = self.get_weather(FORECAST10DAY_KEY)
    forecast = None
    night_forecast = None
    fc_list = forecast_data['forecast']['txt_forecast']['forecastday']
    if day == "today":
      day = datetime.datetime.now().strftime("%A")
    elif day == "tomorrow":
      day = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%A")
    self.log.debug(f"getting weather for day: {day.lower()}")
    for index, temp_forecast in enumerate(fc_list):
      if day.lower() == temp_forecast["title"].lower():
        forecast = temp_forecast
      elif day.lower() + " night" == temp_forecast["title"].lower():
        night_forecast = temp_forecast

    return forecast, night_forecast


  def cmd_get_forecast(self, day="today"):
    """Gets the human readable forecast for the given day.
    Args:
      day (str, optional): The day of the week to get the forecast. "today" and "tomorrow" are also acceptable. 
    Returns:
      bool: True if successful, False otherwise.
      str: Human readable string containing the forecast specified by the day argument.
    """
    try:
      forecast, night_forecast = self.get_forecast(day=day)
      forecast_string = f"Today, {forecast['fcttext']}\nTonight, {night_forecast['fcttext']}"
      if day == "today":
        current_conditions = self.get_current_conditions()
        forecast_string = f"it is currently {current_conditions['temperature']} degrees.\n" + forecast_string
    except network_helpers.NoInternetException:
      return False, ERROR_WEATHER_DATA_NETWORK
    except: # TODO add more exception types
      return False, ERROR_WEATHER_DATA_GENERIC

    if forecast_string is not None:
      return True, forecast_string
    else:
      return False, "problem getting forecast"

  def cmd_get_sunset_time(self):
    """Gets sunset time in a human readable format.
    Returns:
      bool: True if successful, False otherwise.
      str: The human readable time of sunset.
    """

    try:
      sunset_hour, sunset_minute = self.get_sunset_time()
      return True, self.get_readable_time(datetime.datetime.strptime(f"{sunset_hour} {sunset_minute}", "%H %M"))
    except network_helpers.NoInternetException:
      return False, ERROR_WEATHER_DATA_NETWORK
    except: # TODO add more exception types
      return False, ERROR_WEATHER_DATA_GENERIC
    return False, None
 
  def scheduled_good_morning(self):
    """Sends the user a notification to wake up to, containing useful information.
    """
    good_morning_string = "good morning.\n"

    forecast, night_forecast = self.get_forecast()

    good_morning_string += "today's weather.\n"
    good_morning_string += forecast["fcttext"]
    good_morning_string += "\ntonight's weather.\n"
    good_morning_string += night_forecast["fcttext"]

    if "NotificationPlugin" in self.assistant.active_plugins:
      self.log.debug("sending good morning string")
      self.assistant.plugins["NotificationPlugin"].notify(good_morning_string)
    else:
      self.log.warn("notification plugin not active")

