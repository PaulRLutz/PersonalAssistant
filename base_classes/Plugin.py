import os

class Plugin:
  def __init__(self, logger, assistant):
    self.log = logger
    self.log.debug(f"CLASS NAME: {self.__class__.__name__}")
    self._DATA_FOLDER = f"data/{self.__class__.__name__}"
    self._CONFIG_FILE = f"config/plugins/{self.__class__.__name__}.config"
    self.assistant = assistant
    self.status = {}
    self.observable_variables = []

  def DATA_FOLDER(self):
    if not os.path.isdir(self._DATA_FOLDER):
      os.makedirs(self._DATA_FOLDER)
    return self._DATA_FOLDER

  def CONFIG_FILE(self):
    if not os.path.isfile(self._CONFIG_FILE):
      open(self._CONFIG_FILE, "a").close()
    return self._CONFIG_FILE

  def start(self):
    pass

  def stop(self):
    pass

  def refresh_status(self):
    pass

  def get_status(self, refresh=False):
    if refresh:
      self.refresh_status()
    return self.status
