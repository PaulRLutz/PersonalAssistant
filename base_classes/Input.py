
class Input:
  def __init__(self, log, processing_queue):
    self.log = log
    self.processing_queue = processing_queue

  def start(self):
    raise NotImplementedError
  def stop(self):
    raise NotImplementedError


  def send_output(self, output_text, interaction_id):
    raise NotImplementedError

  def get_input(self, prompt_text, interaction_id):
    raise NotImplementedError

  def finished(self, output_text, interaction_id):
    raise NotImplementedError

