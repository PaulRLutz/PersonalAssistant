


class InteractionEngine:
  def __init__(self, logger, assistant):
    self.log = logger
    self.assistant = assistant

  def interaction(self, initial_input, input_object, interaction_id):
    raise NotImplementedError
