from base_classes.Plugin import Plugin

class ScheduledFunctionsPlugin(Plugin):
   
    """Checks to see if there is a connection to the internet, and resets the wireless router if there isn't.
    time_start 
      [
        (-1,-1,-1),
      ]
    time_end
    """
    self.log.debug("checking for internet connection")
    #if "SystemPlugin" in self.assistant.active_plugins and "ArduinoPlugin" in self.assistant.active_plugins:
    #  if not self.assistant.plugins["SystemPlugin"].get_internet_connection_status():
    #    self.log.warn("no internet connection available, resetting router")
    #    self.assistant.plugins["ArduinoPlugin"].cmd_wireless("restart")
    #  else:
    #    self.log.debug("internet connection still available")

 

