"""
  

"""

from threading import Thread
from base_classes.Input import Input
import time
import readline
import os

class TerminalInput(Input):
  def __init__(self, log, assistant):
    self.interaction_id = None
    self.prematurely_finished_interaction_id = None
    self.exit_commands = ["quit"]
    self.log = log
    self.assistant = assistant

    self.LOG_FOLDER = self.assistant.LOG_FOLDER + os.sep + "terminal_input_user_logs"
    if not os.path.exists(self.LOG_FOLDER):
      os.makedirs(self.LOG_FOLDER)

    self.conversation_running = False
    self.load_logged_user_input()

  def start(self):
    self.running = True
    self.thread = Thread(target=self.threaded_function)
    self.thread.start()

  def stop(self):
    self.log.debug("Stopping terminal input")
    self.running = False

  def threaded_function(self):
    while self.running:
      time.sleep(.25)
      if self.interaction_id is None:
        user_input = self.get_input("", None)
        self.log_user_input(user_input)
        self.interaction_id = self.assistant.new_user_input(user_input, input_object=self)
        self.log.debug(f"setting new interaction_id: {self.interaction_id}")
        if self.interaction_id == self.prematurely_finished_interaction_id:
          self.interaction_id = None
          self.prematurely_finished_interaction_id = None

  def send_output(self, output_text, interaction_id):
    output_text = str(output_text)
    output_text = output_text.replace('\n', '\n\t')
    print("\n***************************************")
    print(f"\t{output_text}")
    print("***************************************\n")

  def get_input(self, prompt_text, interaction_id):
    self.log.debug(f"Waiting for user input (interaction_id={interaction_id})")
    if self.interaction_id is not None:
      conversation_active = "@"
    else:
      conversation_active = " "
    new_user_input = input(f"{conversation_active}>>> ")
    self.log.debug(f"New user input: '{new_user_input}'")
    return new_user_input

  def finished(self, output_text, interaction_id):
    self.log.debug(f"Finishing interaction with id: {interaction_id}")
    if self.interaction_id is None:
      self.log.warn("interaction ended before interaction_id was set")
      self.prematurely_finished_interaction_id = interaction_id
    self.interaction_id = None
    self.send_output(output_text, None)

  def log_user_input(self, user_input):
    """
      Logs the user input into a file based on the session number
    """
    try:
      if self.previous_user_input == user_input:
        self.log.debug("don't dual-log commands")
        return
      else:
        self.previous_user_input = user_input
    except AttributeError:
      self.previous_user_input = user_input

    log_file_name = self.LOG_FOLDER + os.sep + str(self.assistant.session_number)
    with open(log_file_name, "a") as log_file:
      log_file.write(str(user_input) + "\n")

  def load_logged_user_input(self):
    """
      Loads the user input form the log files
    """
    log_files = os.listdir(self.LOG_FOLDER)
    log_files = [str(a) for a in sorted([int(b) for b in log_files])]

    for log_file in log_files:
      readline.read_history_file(self.LOG_FOLDER + os.sep + log_file)
