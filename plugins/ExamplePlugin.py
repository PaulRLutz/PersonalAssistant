from base_classes.Plugin import Plugin

class ExamplePlugin(Plugin):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
 
    self.moods = ["happy", "sad"]
    self.mood = self.moods[0]

    self.observable_variables.append(self.mood)

  """Simple command that changes the mood variable
    Returns:
      bool: True if successfull, False otherwise.
      str: String validating the choice
  """
  def cmd_set_mood(self, new_mood):
    if new_mood in self.moods:
      self.mood = new_mood
      return True, f"New mood set to: '{self.mood}'"
    else:
      return False, f"Mood '{new_mood}' is not an available mood"

  """Simple command that says hello to the user.
  Returns:
    bool: True if successfull, False otherwise.
    str: String containing "hello".
  """
  def cmd_hello(self):
    return True, "hello, how are you"

  """Simple command that says hello to the user.
    Returns:
      bool: True if successfull, False otherwise.
      str: String containing the name of the assistant.
  """
  def cmd_name(self):
    return True, f"my name is {self.assistant.main_config_dict['main']['name']}"
