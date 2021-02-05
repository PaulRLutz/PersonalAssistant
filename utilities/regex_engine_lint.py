"""
todo:
  regex errors?
  proper command variable names
  regex conflicts
  misspellings

in progress:

finished:
  unused commands
  links for nonexistent commands
  COMMANDS ARE NOT UNIQUE KEYS THEY CAN HAVE MULTIPEL KEYS (dumbass)

"""
import pprint
import sys
import os
sys.path.insert(0, os.path.abspath('..')) # Fuck you python 3
from interaction_engines.RegexConversationInteractionEngine import Dialogue, DialoguePiece, TextTemplate, Argument
from helpers.yaml_parser import parse_yaml_file
import importlib

def get_all_links():
  links_folder = "../config/links"
  links_list = []
  for links_file in os.listdir(links_folder):
    if links_file.endswith("links.yaml"):
      links_list.extend(parse_yaml_file(f"{links_folder}/{links_file}"))
  return links_list

def get_all_commands(plugin_name=None):
  all_commands = {} # format: {plugin_name: [cmd1_name, cmd2_name, ...], ...}
  plugins_folder = "../plugins"
  for plugin_file in os.listdir(plugins_folder):
    if plugin_file.endswith("Plugin.py"):
      plugin_name = plugin_file[:plugin_file.index(".")]
      plugin = importlib.import_module("plugins." + plugin_name)
      plugin_object = getattr(plugin, plugin_name)
      if plugin_name not in all_commands:
        all_commands[plugin_name] = []
      for function_name in dir(plugin_object):
        if function_name.startswith("cmd_"):
          all_commands[plugin_name].append(function_name)

  return all_commands

def print_command(links_data):
  # TODO implement
  pass

def get_unlinked_commands(commands_data, commands_links_data):
  for plugin_name, commands in commands_data.items():
    plugin_present = False
    for command_link in commands_links_data:
      if command_link[0] == plugin_name:
        plugin_present = True
    if not plugin_present:
      print(f"Plugin does not exist in links: '{plugin_name}'")
    for command_name in commands:
      command_present = False
      for command_link in commands_links_data:
        if command_link[1] == command_name:
          command_present = True
      if not command_present:
        print(f"No link to command: '{command_name}', in plugin: '{plugin_name}'")
     
def get_orphaned_links(commands, commands_links_data):
  for command_link in commands_links_data:
    plugin_name = command_link[0]
    command_name = command_link[1]
    if plugin_name not in commands:
      print(f"Link to nonexistent plugin: '{plugin_name}'")
    else:
      if command_name not in commands[plugin_name]:
        print(f"Link to nonexistent command: '{command_name}' in plugin: '{plugin_name}'")

def spacer(level=1):
  return "  "*level
def print_links_data(commands_links_data, print_text_templates=True):
  links_dict = {}
  for link in commands_links_data:
    if link[0] not in links_dict.keys():
      links_dict[link[0]] = {}
    if link[1] not in links_dict[link[0]].keys():
      links_dict[link[0]][link[1]] = []
    links_dict[link[0]][link[1]].append(link[2])

  for plugin_name, commands_dict in links_dict.items():
    print(f"spacer(1)Plugin: {plugin_name}")
    for command_name, dialogues in commands_dict.items():
      print(f"{spacer(2)}Command: {command_name}")
      for index, dialogue in enumerate(dialogues):
        print(f"{spacer(3)}Dialogue num: {index+1}")
        for dialogue_piece in dialogue:
          if print_text_templates:
            for text_template_index, text_template in enumerate(dialogue_piece.text_templates):
              print(f"{spacer(4)}text template: {text_template_index}")
              print(f"{spacer(5)}regex string: {text_template.regex_string}")
              if text_template.arg_list is not None:
                print(f"{spacer(5)}arguments:")
                for argument in text_template.arg_list:
                  print(f"{spacer(6)}{argument}")
def main():
  commands_links_data = get_all_links()
  commands_data = get_all_commands()
 
  get_unlinked_commands(commands_data, commands_links_data)  
  get_orphaned_links(commands_data, commands_links_data)
  #print_links_data(commands_links_data)

if __name__ == "__main__":
  main()

