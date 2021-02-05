import yaml
import collections

Dialogue = collections.namedtuple("Dialogue", "plugin_name command dialogue_pieces")
DialoguePiece = collections.namedtuple("DialoguePiece", "prompt text_templates output")
TextTemplate = collections.namedtuple("TextTemplate", "regex_string arg_list")
Argument = collections.namedtuple("Argument", "name arg_type regex_index")

PLUGIN_KEY = "plugin"
COMMAND_KEY = "command"
PROMPT_KEY = "prompt"
OUTPUT_KEY = "output"
TEXT_TEMPLATES_KEY = "text_templates"
REGEX_STRING_KEY = "regex_string"
ARGUMENTS_KEY = "arguments"
ARG_NAME_KEY = "name"
ARG_TYPE_KEY = "type"
ARG_INDEX_KEY = "regex_index"
DIALOGUE_PIECES_KEY = "dialogue_pieces"

def parse_yaml_file(yaml_file_name):

  yaml_data_map = {}

  with open(yaml_file_name, "r") as yaml_file:
    yaml_data_map = yaml.safe_load(yaml_file)

  plugin_name = None
  command_name = None

  pre_dialogue_list = []

  for convo_name, conversation in yaml_data_map.items():
    plugin_name = conversation[PLUGIN_KEY]
    command_name = conversation[COMMAND_KEY]
    dialogue_pieces = get_dialogue_pieces(conversation[DIALOGUE_PIECES_KEY])
    pre_dialogue_list.append((plugin_name, command_name, dialogue_pieces))

  return pre_dialogue_list

def get_dialogue_pieces(dialogue_pieces_list):

  dialogue_pieces = []

  for dialogue_dict in dialogue_pieces_list:
    prompt = None
    text_templates = None
    output = None
    try:
      prompt = dialogue_dict[PROMPT_KEY]
    except KeyError:
      pass
    try:
      output = dialogue_dict[OUTPUT_KEY]
    except KeyError:
      pass
    text_templates = get_text_templates(dialogue_dict[TEXT_TEMPLATES_KEY])
    dialogue_pieces.append(DialoguePiece(prompt=prompt, text_templates=text_templates, output=output))

  return dialogue_pieces

def get_text_templates(text_templates_list):

  text_templates = []

  for text_template_dict in text_templates_list:
    regex_string = None
    arguments = None
    try:
      regex_string = text_template_dict[REGEX_STRING_KEY]
    except KeyError:
      pass
    try:
      arguments = get_arguments(text_template_dict[ARGUMENTS_KEY])
    except KeyError:
      pass
    text_templates.append(TextTemplate(regex_string=regex_string, arg_list=arguments))

  return text_templates

def get_arguments(arguments_list):

  arguments = []

  for argument_dict in arguments_list:
    arg_name = None
    arg_type = None
    arg_index = None

    try:
      arg_name = argument_dict[ARG_NAME_KEY]
    except KeyError:
      pass
    try:
      arg_type = argument_dict[ARG_TYPE_KEY]
    except KeyError:
      pass
    try:
      arg_index = argument_dict[ARG_INDEX_KEY]
    except KeyError:
      pass
    arguments.append(Argument(name=arg_name, arg_type=arg_type, regex_index=arg_index))

  return arguments

def main():
  parse_yaml_file("links.yaml")

if __name__ == "__main__":
  main()
