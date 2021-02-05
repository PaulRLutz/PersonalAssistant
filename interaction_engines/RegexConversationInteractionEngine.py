import os
import re
import traceback
import collections
from base_classes.InteractionEngine import InteractionEngine
from helpers.yaml_parser import parse_yaml_file, Dialogue, DialoguePiece, TextTemplate, Argument

class RegexConversationInteractionEngine(InteractionEngine):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.LINKS_FOLDER = "config/links"
    self.load_dialogues()

  def load_dialogues(self):
    """
      Loads all dialogues from links.yaml.
    """
    self.dialogues = []
    pre_dialogue_list = []
    for config_file in os.listdir(self.LINKS_FOLDER): 
      if config_file.endswith("links.yaml"):
        self.log.debug(f"found config file: {config_file}")
        pre_dialogue_list.extend(parse_yaml_file(f"{self.LINKS_FOLDER}/{config_file}"))
    for pre_dialogue in pre_dialogue_list:
      if pre_dialogue[0] not in self.assistant.active_plugins:
        continue
      self.log.debug(f"loading dialogue with plugin name: {pre_dialogue[0]} and function name: {pre_dialogue[1]}")
      self.dialogues.append(Dialogue(plugin_name=pre_dialogue[0],
                                     command=pre_dialogue[1],
                                     dialogue_pieces=pre_dialogue[2]))

  def interaction(self, initial_input, input_object, interaction_id):
    """
      Handles a dialogue to get the arguments necessary for the given command.
    """

    dialogue = self.get_matching_dialogue(initial_input)
    if dialogue is None:
      self.log.debug(f"couldn't find matching dialogue for input: '{initial_input}'")
      input_object.finished("sorry, i can't help with that", interaction_id)
      return

    extracted_arguments = {}
    if dialogue.dialogue_pieces is not None:
      for index, dialogue_piece in enumerate(dialogue.dialogue_pieces):
        if index == 0:
          user_input = initial_input
        else:
          user_input = input_object.get_input(dialogue_piece.prompt, interaction_id)
        attempts = 1
        
        while True:
          process_success, new_extracted_arguments = self.process_input(user_input, dialogue_piece.text_templates)

          if process_success:
            extracted_arguments = {k: v for d in [extracted_arguments, new_extracted_arguments] for k, v in d.items()}
            break
          else:
            self.log.warn("problem processing user input")
          if attempts > MAX_ATTEMPTS:
            self.log.error("max attempts reached")
            input_object.finished("sorry, there was some error", interaction_id)
            return
          
          attempts += 1
          user_input = input_object.get_input("sorry, i missed that. " + dialogue_piece.prompt, interaction_id)
        
        if dialogue_piece.output is not None and dialogue_piece.output != "":
          input_object.send_output(dialogue_piece.output, interaction_id)
    
    # TODO Add check to see if extracted_arguments has all of the necessary arguments
    try:
      plugin = self.assistant.plugins[dialogue.plugin_name]
      func = getattr(plugin, dialogue.command)
      success, output_text = self.assistant.execute_command(func, extracted_arguments)    
    except:
      success = False
      output_text = "problem executing command, check log"
      self.log.error(output_text)
      self.log.error(traceback.format_exc())

    input_object.finished(output_text, interaction_id)

  def process_input(self, input_text, text_templates):
    """
      Gets the named arguments from the given input text, based on the given text templates.
    """
    extracted_arguments = {}
    if text_templates is None:
      self.log.warn("Dialogue piece has no text templates")
      return False, {}
    for text_template in text_templates:
      self.log.debug(f"Processing input text: '{input_text}', and input text template: '{text_template}'")
      matched = re.compile(text_template.regex_string).findall(input_text)
      if isinstance(matched, tuple): # If it is not a string, then it's a list and the first item is what we need.
        matched = matched[0]
      if text_template.arg_list is None: # if the text template arg list is empty, then there are no args to process
        self.log.debug("no arg_list, so we're good")
        return True, {}
      if len(matched) < len(text_template.arg_list):
        self.log.error("did not get enough arguments")
        continue
      for argument in text_template.arg_list:
        raw_argument = matched[argument.regex_index]
        arg_processing_success, processed_argument = self.process_argument_for_type(raw_argument, argument.arg_type)
        if arg_processing_success:
          extracted_arguments[argument.name] = processed_argument
        else:
          self.log.error(f"error processing argument {raw_argument} of type {argument.arg_type}")
          continue
      return True, extracted_arguments
    self.log.warn(f"Couldn't find matching text template for input: {input_text}")
    return False, {}

  def process_argument_for_type(self, raw_argument, arg_type):
    # TODO implement
    return True, raw_argument



  def get_matching_dialogue(self, input_text):
    """
      Find the dialogue that matches the given input text.
    """
    for dialogue in self.dialogues:
      if dialogue.dialogue_pieces is not None and len(dialogue.dialogue_pieces) > 0:
        for text_template in dialogue.dialogue_pieces[0].text_templates:
          matched = re.compile(text_template.regex_string).findall(input_text)
          if len(matched) > 0:
            return dialogue
    return None


