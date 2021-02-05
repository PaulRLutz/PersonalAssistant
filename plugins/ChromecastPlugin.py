from base_classes.Plugin import Plugin
import pychromecast
from helpers.text2num.text2num import text2num, NumberException


class ChromecastPlugin(Plugin):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.update_chromecast_list()
    
  def update_chromecast_list(self):
    self.chromecasts = pychromecast.get_chromecasts()


  def get_default_chromecast(self):
    for chromecast in self.chromecasts:
      if chromecast.device.friendly_name == self.assistant.chromecast_plugin_config_dict["main"]["default_chromecast_name"]:
        return chromecast
    return None

  def cmd_chromecast_play_pause(self, command):
    chromecast = self.get_default_chromecast()
    if chromecast is not None:
      if command == "play":
        chromecast.media_controller.play()
        return True, "chromecast play"
      elif command == "pause":
        chromecast.media_controller.pause()
        return True, "chromecast pause"
      else:
        return False, f"chromecast command {command} not recognized"
    else:
      return False, "couldn't find default chromecast"

  def cmd_chromecast_seek(self, seek_seconds):
    chromecast = self.get_default_chromecast()
    if chromecast is not None:
      try:
        seek_seconds = int(seek_seconds)
      except ValueError:
        self.log.warn("chromecast seek seconds is not an integer")
      try:
        seek_seconds = text2num(seek_seconds)
      except NumberException:
        return False, "chromecast seek value must be an integer"
      chromecast.media_controller.seek(seek_seconds)
      return True, "seeking"
    else:
      return False, "couldn't find default chromecast"

