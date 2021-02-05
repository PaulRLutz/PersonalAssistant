import logging
from datetime import datetime

class CustomLogHandler(logging.StreamHandler):
  def __init__(self, log_file_name=None, *args, **kwargs):
    super(CustomLogHandler, self).__init__(*args, **kwargs)
    self.log_file_name = log_file_name

  def emit(self, record):
    log_message = self.clean_log_message(record.msg)
    time_string = datetime.now().strftime("%Y-%m-%d %I:%M:%S")
    log_string = f"{record.levelname}|{time_string}|{record.filename}|{record.lineno}|{record.funcName}|{log_message}"
    with open(self.log_file_name, "a+") as log_file:
      log_file.write(log_string + "\n")
  
  def clean_log_message(self, log_message):
    log_message = str(log_message).replace("\n", "<newline>")
    return log_message
