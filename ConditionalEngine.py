"""
  TODO:
    Make sure conditions only fire once
    Conditional should be able to compare DATA with its previous value!
    
"""

"""
  Flow:
      

  Conditional item structure:
    dict: {PLUGIN_KEY, DATA_KEY, DATA, TARGET_DATA, DATA_COMPARISON} 
    conditional: {"CONDITIONS": [condition1,condition2,...], "ACTION" : <METHOD>, "RESET_CONDITIONS" : [condition3,condition4,...]}

  Queue item structure:
   dict: {TIME, PLUGIN_KEY, DATA_KEY, DATA}
"""
import sqlite3




class ConditionalEngine:
  def __init__(self, logger, assistant):
    self.log = logger
    self.assistant = assistant

    self.conditional_thread = Thread(target=self.conditional_thread_function)
    self.conditions = None # TODO load conditions
    self.sqlite_file = "db.db"

  def get_db(self):
    conn = sqlite3.connect(self.sqlite_file)

  def conditional_thread_function(self):
    while self.assistant.running:
      if not self.conditional_queue.empty():
        conditional = self.conditional_queue.pop()

  def start(self):
    self.scheduled_thread.start()

  """
  Queue item structure:
    dict: {TIME, PLUGIN_KEY, DATA_KEY, DATA}

    1. Get item from queue
    2. store new data in storage
    3. check if a conditional is active that subscribes to the data key
      a. check if the conditional matches the updated data from queue
      b. If conditional matches, check if it has other requirements
      c. If other requirements match, preform conditional action
      d. Activate conditional reset conditions
    4. if no conditionals match, do nothing
    
  """
  def process_queue_item(self, item):
    self.store_new_data_item(item)
    
    for conditional in self.get_active_conditionals(item):
      for condition in conditional["CONDITIONS"]:
        if not self.check_conditional(condition):
          self.log.debug("Condition isn't")
          break
      else:
        self.log.debug("All conditions met, performing conditional action")
        self.execute_conditional_action(conditional)
        self.disable_conditional(conditional)
        self.enable_conditional_reset(conditional)

  def enable_conditional_reset(self, conditional):
    pass # TODO implement

  def disable_conditional(self, conditional):
    pass # TODO implement

  def execute_conditional_action(self, conditional):
    pass # TODO implement

  def store_new_data(self, item):
    pass # TODO implement

  def get_active_conditionals(self, item):
    return [] # TODO implement
