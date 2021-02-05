from base_classes.InteractionEngine import InteractionEngine

class CLIInteractionEngine(InteractionEngine):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
    self.command_dict = {}


  def get_all_commands(self, plugin):
    func = getattr(plugin, pre_dialogue[1])
    return

  def interaction(self, initial_input, input_object, interaction_id):
    if initial_input is None:
      input_object.finished("no initial input received", interaction_id)
    input_list = initial_input.split(" ")
    if len(input_list) < 1:
      input_object.finished("no initial input received", interaction_id)
    plugin_name = input_list.pop(0)
