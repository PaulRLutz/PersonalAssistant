from base_classes.Plugin import Plugin
import subprocess
import psutil
import socket

STATUS_CPU_USAGE_KEY = "cpu_usage"
STATUS_CPU_TEMP_KEY = "cpu_temp"
STATUS_RAM_USAGE_KEY = "ram_usage"

class SystemPlugin(Plugin):

  def refresh_status(self):
    """Populates the self.status dict."""
    self.status[STATUS_CPU_USAGE_KEY] = psutil.cpu_percent()
    self.status[STATUS_CPU_TEMP_KEY] = self.get_cpu_temp()
    self.status[STATUS_RAM_USAGE_KEY] = psutil.virtual_memory()[2]

  # TODO Be less lazy. No empty except, check more than just google.
  def get_internet_connection_status(self):
    """Gets whether this is a working internet connection
    Returns:
      bool: True if there is an internet connection, False otherwise.
    """
    try:
      host = socket.gethostbyname("www.google.com")
      s = socket.create_connection((host, 80), 1)
      return True
    except:
      return False

  def cmd_get_cpu_temp(self):
    """Gets the cpu temp.
    Returns:
      bool: True if successful, False otherwise.
      str: Human readable cpu temperature.
    """
    cpu_temp = self.status[STATUS_CPU_TEMP_KEY]

    if cpu_temp is None:
      return False, "there was a problem getting the processor temperature"
    else:
      return True, f"the processor temperature is {cpu_temp} degrees"

  def get_cpu_temp(self):
    """Gets the cpu temp.
    Returns:
      str: The CPU temperature, None if there was a problem.
    """
    cpu_sensor_name = "coretemp-isa-0000"
    total_temp = 0.0
    temp_count = 0.0
    for sensor_dict in self.get_sensors_dict_list():
      if sensor_dict["name"] == cpu_sensor_name:
        for key in sensor_dict.keys():
          if "temp" in key or "Core" in key:
            total_temp += float(sensor_dict[key])
            temp_count += 1
        return total_temp/temp_count
    return None

  def cleanup_temp(self, temp_line):
    """Cleans up the temperature received from the sensors command
    Args:
      str: The line from the sensors command that contains the temperature. 
    Returns:
      str: Cleaned up temperature.
    """
    temp_string = temp_line.strip().split(" ")[0]
    return temp_string[1:-2]

  def get_sensors_dict_list(self):
    """Gets the  list of dicts of sensors.
    Returns:
      list: The list of dicts. Dicts contain the name, adapter, and temperatures of the sensor.
    """
    raw = (subprocess.check_output(["sensors"])).decode("utf-8") 
    string_list = raw.split("\n\n")
    d_list = []
    for d_string in string_list:
      d_string_list = d_string.split("\n")
      if len(d_string_list) < 3:
        break
      d = {}
      d["name"] = d_string_list[0]
      d["adapter"] = d_string_list[1].split(":")[1]
      for prop_line in d_string_list[2:]:
        try:
          d[prop_line.split(":")[0]] = self.cleanup_temp(prop_line.split(":")[1])
        except IndexError:
          pass # this just isn't a sensor line, don't worry about it.
      d_list.append(d)
  
    return d_list

  def scheduled_wireless_check(self):
    if not self.get_internet_connection_status():
      self.log.warn("no internet connection available, resetting router")
      if "ArduinoPlugin" in self.assistant.active_plugins:
        self.assistant.plugins["ArduinoPlugin"].cmd_wireless("restart")
      else:
        self.log.warn("Arduino plugin not active")
    else:
      self.log.debug("internet connection still available")

 
