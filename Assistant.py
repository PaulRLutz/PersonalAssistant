import os
import importlib
import logging as log
from threading import Thread
import time
import configparser
import traceback
import json
import uuid
import sys
import datetime
from helpers.CustomLogHandler import CustomLogHandler

PLUGIN_TYPE = "plugin"
INPUT_TYPE = "input"
INTERACTION_ENGINE_TYPE = "interaction_engine"

class Assistant:
  def __init__(self, logger):
    self.LOG_FOLDER = "logs"
    self.log = logger

    # create log folder if it doesn't exist
    if not os.path.exists(self.LOG_FOLDER):
      os.makedirs(self.LOG_FOLDER)

    # generate the session number
    self.generate_session_number()

    custom_log_handler = CustomLogHandler(log_file_name=f"{self.LOG_FOLDER}{os.sep}main{os.sep}{self.session_number}.log")

    self.log = self.log.getLogger()
    self.log.addHandler(custom_log_handler)
    self.log.setLevel(log.DEBUG)

    config_folder = os.path.dirname(os.path.realpath(__file__)) + os.sep + "config"
    self.load_config_files(config_folder=config_folder)
    credentials_folder = os.path.dirname(os.path.realpath(__file__)) + os.sep + "credentials"
    self.load_config_files(config_folder=credentials_folder, var_concat="credentials_dict")

    self.status_dict = {}
    self.status_last_refresh_time_dict = {"default" : 0}

    self.scheduled_functions = {}

    self.plugin_modules = {}
    self.plugins = {}
    self.plugins["default"] = self # TODO remove constant
    self.active_plugins = ["default"] 

    self.interaction_engines = {}

    self.active_inputs = []
    self.inputs = {}
    
    self.running = True
    self.interactions = []

  def generate_session_number(self):
    """Populates the self.session_number value. 

    Basically just loads the session number, increments it, and writes it back to the log file.
    """
    session_number_file_name = f"{self.LOG_FOLDER}{os.sep}session_number.log"
    if not os.path.exists(session_number_file_name):
      self.session_number = 0
    else:
      with open(session_number_file_name, "r") as session_number_file:
        self.session_number = int(session_number_file.readline().strip()) + 1
    with open(session_number_file_name, "w") as session_number_file:
      session_number_file.write(str(self.session_number))

  def load_config_files(self, config_folder=None, config_file=None, var_concat="config_dict"):
    if config_folder is not None: 
      config_files = os.listdir(config_folder)
      config_files = [file_name for file_name in os.listdir(config_folder) if file_name.endswith(".config")]
    elif config_file is not None:
      config_files = [config_file]
    else:
      return
    
    for config_file in config_files:
      config_dict_name = config_file.split(".")[0] + "_" + var_concat
      setattr(self, config_dict_name, self.config_to_dict(config_folder + os.sep + config_file))

  # https://stackoverflow.com/a/3220740
  def config_to_dict(self, file_path):
    config = configparser.ConfigParser({})
    config.read(file_path)
    dictionary = {}
    for section in config.sections():
      dictionary[section] = {}
      for option in config.options(section):
        dictionary[section][option] = self.cast_config_value(config.get(section, option))
    return dictionary

  # https://stackoverflow.com/a/15357477
  def cast_config_value(self, config_value):
    try:
      a = int(config_value)
      b = float(config_value)
      if a == b: # If float equals int, then it's an int, otherwise it's a float
        return a
      else:
        return b
    except ValueError: # If it's neither a float or an int, then it's a string
      return config_value

  def load_objects(self):
    all_files = {
        "plugins" : os.listdir("plugins"),
        "inputs"  : os.listdir("inputs"),
        "interaction_engines" : os.listdir("interaction_engines"),
        }
    for folder_name, files in all_files.items():
      for file_name in files: 
        obj_type = self.get_object_type_from_file_name(file_name)
        if obj_type is not None:
          obj_name = file_name[:file_name.index(".")]
          if obj_name.lower() not in self.main_config_dict[f"{obj_type}s"]:
            self.log.debug(f"{obj_name} not listed, don't load it")
            continue
          if self.main_config_dict[f"{obj_type}s"][obj_name.lower()] == "False":
            self.log.debug(f"{obj_name} not active, don't load it")
            continue
          self.log.debug(f"Loading {obj_type}: {obj_name}")
          try:
            obj_module = importlib.import_module(folder_name + "." + obj_name)   # Import the plugin module
          except:
            import_error_text = traceback.format_exc()   
            self.log.warn(f"problem importing {obj_type} {obj_name}")
            self.log.warn(import_error_text)
            continue

          obj = getattr(obj_module, obj_name)
          if obj_type is INPUT_TYPE:
            try:
              self.inputs[obj_name] = obj(self.log, self)
              self.inputs[obj_name].start()
              self.active_inputs.append(obj_name)
            except:
              obj_start_error_text = traceback.format_exc()   
              self.log.warn(f"problem starting {obj_type} {obj_name}")
              self.log.warn(obj_start_error_text)
          elif obj_type is PLUGIN_TYPE:
            self.load_plugin(obj_name, obj, obj_module)
          if obj_type is INTERACTION_ENGINE_TYPE:
            self.interaction_engines[obj_name] = obj(self.log, self)

  def reload_plugin(self, plugin_name):
    if plugin_name == "default":
      return False, "don't reload default"

    # stop the plugin
    if plugin_name in self.active_plugins:
      try:
        self.plugins[plugin_name].stop()
      except:
        error_message = f"there was a problem stopping plugin {plugin_name}"
        self.log.error(error_message)
        self.log.error(traceback.format_exc())
        return False, error_message
    else:
      return False, f"plugin {plugin_name} unavailable"

    # reload the plugin module
    try:
      importlib.reload(self.plugin_modules[plugin_name])
    except:
      error_message = f"there was a problem reloading plugin {plugin_name}"
      self.log.error(error_message)
      self.log.error(traceback.format_exc())
      return False, error_message
    
    del self.plugins[plugin_name] # delete the stopped plugin
    plugin_object = getattr(self.plugin_modules[plugin_name], plugin_name) # get the plugin object from the module
    return self.load_plugin(plugin_name, plugin_object, self.plugin_modules[plugin_name]) # load the plugin like normal
      
  def load_plugin(self, plugin_name, plugin_object, plugin_module):
    self.plugin_modules[plugin_name] = plugin_module
    try:
      self.plugins[plugin_name] = plugin_object(self.log, self)
      self.status_last_refresh_time_dict[plugin_name] = 0
      self.plugins[plugin_name].start()
      self.active_plugins.append(plugin_name)
      self.load_plugin_scheduled_functions(plugin_name)
    except:
      plugin_start_error_text = traceback.format_exc()   
      self.log.warn(f"problem starting plugin {plugin_name}")
      self.log.warn(plugin_start_error_text)
      return False, plugin_start_error_text
    return True, f"plugin {plugin_name} loaded successfully"

  def get_object_type_from_file_name(self, file_name):
    if file_name.endswith("Input.py"):
      return INPUT_TYPE
    elif file_name.endswith("Plugin.py"):
      return PLUGIN_TYPE
    elif file_name.endswith("InteractionEngine.py"):
      return INTERACTION_ENGINE_TYPE
    else:
      return None


  def new_user_input(self, initial_input, input_object, engine_name=None):
    if engine_name is None:
      engine_name = self.main_config_dict["main"]["default_interaction_engine"]
    interaction_id = uuid.uuid4()
    if len(self.interactions) > self.main_config_dict["main"]["max_interactions"]:
      # TODO warn user
      pass # TODO Auto-end
    else:
      if engine_name not in self.interaction_engines:
        self.log.debug(f"couldn't find matching interaction engine: {engine_name}")
        input_object.finished(False, "engine configuration error")
        return
      else:
        new_interaction_thread = Thread(target=self.interaction_engines[engine_name].interaction, args=(initial_input, input_object, interaction_id,))
      
      new_interaction_thread.start()
      self.interactions.append(new_interaction_thread)
      return interaction_id
    return None

  # TODO add generic try/catch
  def execute_command(self, command, arguments):
    self.log.debug(f"Attempting to execute command: {str(command)}, with args: {arguments}")
    return command(**arguments)


  def print_plugins(self):
    for plugin_name, plugin in self.plugins.items():
      print(f"{plugin_name}")

  def print_dialogues(self):
    for dialogue in self.dialogues:
      print(f"plugin name: {dialogue.plugin_name}")

  def cmd_reload_plugin(self, plugin_name):
    return self.reload_plugin(plugin_name)

  def cmd_quit(self):
    """Quits the Assistant
    Returns:
      bool: True if successful, False otherwise
      str: "shutting down"
    """
    for input_name, input_object in self.inputs.items():
      input_object.stop()
    for plugin_name, plugin_object in self.plugins.items():
      if plugin_name != "default": # TODO remove constant
        plugin_object.stop()
    self.running = False

    return True, "shutting down"

  def cmd_status(self):
    """Shows the contents of the status dict.
    Returns:
      bool: True if successful, False otherwise.
      str: The contents of the status dict.
    """
    final_string = ""
    for plugin_name, status_dict in self.status_dict.items():
      final_string += plugin_name + "\n"
      final_string += "\tlast refresh: " + str(self.status_last_refresh_time_dict[plugin_name]) + "\n"
      for status_item, status_value in status_dict.items():
        final_string += f"\t{status_item} is {status_value}\n"
    return True, final_string

  def load_plugin_scheduled_functions(self, plugin_name):
    """Loads the scheduled functions."""

  DAYS_OF_WEEK_KEY = "days_of_week"
  DAYS_OF_MONTH_KEY = "days_of_month"
  TIMES_KEY = "times"
  COMMAND_KEY = "cmd"

  def scheduled_thread(self):
    """Once approximately every 60 seconds, runs any scheduled functions with a matching time."""
    self.previous_timestamp = -1
    while self.running:
      time.sleep(3)
      current_time = datetime.datetime.now()
      current_time = current_time.replace(second=0)
      if current_time.timestamp() - self.previous_timestamp <= 60: # if at least 60 seconds haven't passed, don't do anything
        continue
      else:
        self.previous_timestamp = current_time.timestamp()
        self.log.debug(f"checking scheduled functions at timestamp: {self.previous_timestamp}")

      current_minute = current_time.minute
      current_hour = current_time.hour
      current_weekday = current_time.weekday()
      current_day_of_month = current_time.day
      current_month = current_time.month

      for plugin_name, scheduled_functions in self.scheduled_functions.items():
        for scheduled_function in scheduled_functions:
          if (current_hour, current_minute) not in scheduled_function[TIMES_KEY]:
            self.log.debug(f"Not the right time for scheduled function {scheduled_function['name']}")
            continue
          if DAYS_OF_WEEK_KEY in scheduled_function:
            if not current_weekday in scheduled_function[DAYS_OF_WEEK_KEY]:
              self.log.debug(f"Not the right weekday for scheduled function {scheduled_function['name']}")
              continue
              self.log.debug(f"Running scheduled function {scheduled_function['name']}")
          elif DAYS_OF_MONTH_KEY in scheduled_function:
            if not current_day_of_month in scheduled_function[DAYS_OF_MONTH_KEY]:
              self.log.debug(f"Not the right day of month for scheduled function {scheduled_function['name']}")
              continue

          self.log.debug(f"Running scheduled function {scheduled_function['name']}")
          scheduled_function[COMMAND_KEY]()

  
  def status_thread(self):
    while self.running:
      for plugin_name, plugin in self.plugins.items():
        time_seconds = time.time()
        if time_seconds - self.status_last_refresh_time_dict[plugin_name] > self.status_config_dict[plugin_name]["refresh_interval"]:
          try:
            self.status_last_refresh_time_dict[plugin_name] = time_seconds
            self.status_dict[plugin_name] = plugin.get_status(refresh=True)
          except:
            self.log.error(f"problem getting status from plugin: {plugin_name}")
            self.log.error(traceback.format_exc())
      time.sleep(.5)

  def get_status(self, refresh=False):
    TIME_KEY = "time"
    DATE_KEY = "date"

    time_value = time.strftime("%I:%M:%S %p")
    date_value = time.strftime("%B %d, %Y")

    return { TIME_KEY : time_value, DATE_KEY : date_value }


  def start(self):
    self.scheduled_thread = Thread(target=self.scheduled_thread)
    self.scheduled_thread.start()

    self.status_thread = Thread(target=self.status_thread)
    self.status_thread.start()
    finished_thread_indices = []
    try:
      while self.running:
        time.sleep(.1)
        for index, interaction_thread in enumerate(self.interactions):
          if not interaction_thread.isAlive():
            interaction_thread.join()
            finished_thread_indices.append(index)
        if len(finished_thread_indices) > 0:
          self.log.debug(f"Removing threads with indices: {finished_thread_indices}")
          self.interactions = [convo for index, convo in enumerate(self.interactions) if index not in finished_thread_indices]
          finished_thread_indices = []
    except KeyboardInterrupt:
      self.running = False
      self.cmd_quit()

def main():
  assistant = Assistant(log)
  assistant.load_objects()
  assistant.start()

if __name__ == "__main__":
  main()
