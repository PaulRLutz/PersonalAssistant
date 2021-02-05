from base_classes.InteractionEngine import InteractionEngine
from snips_nlu import SnipsNLUEngine, load_resources
import subprocess
import io
import json
import os
import time

class SnipsNluInteractionEngine(InteractionEngine):
  def __init__(self, logger, assistant):
    self.log = logger
    self.assistant = assistant

    self.generate_dataset_file = "/home/paul/Workspaces/Multi/Assistant/Python/utilities/snips_generate_dataset_wrapper.py"
    self.training_data_folder = "/home/paul/Workspaces/Multi/Assistant/Python/config/snips"
    self.dataset_file = f"{self.training_data_folder}" + os.sep + "dataset.json"

    self.regenerate_dataset()
    time.sleep(3) # TODO handle this better
    self.load_dataset()

  def interaction(self, initial_input, input_object, interaction_id):
    self.log.debug(f"Snips processing user input: '{initial_input}'")
    snips_parsed_dict = self.engine.parse(initial_input)
    self.log.debug("Parsed data:")
    self.log.debug(str(snips_parsed_dict))
    self.log.debug(str(type(snips_parsed_dict)))

    if snips_parsed_dict == None:
      error_message = "Snips parsed dict is None"
      self.log.error(error_message)
      input_object.finished(error_message, interaction_id)
      return
    elif snips_parsed_dict["intent"] == None:
      self.log.error("No intent in snips parsed dict, unrecognized command")
      input_object.finished("sorry, i can't help with that", interaction_id) # TODO make an "unrecognized command response"
      return


    output_text = snips_parsed_dict["slots"][0]["rawValue"] + ": " + str(snips_parsed_dict["intent"]["probability"])
    output_text = "HI"
    input_object.finished(output_text, interaction_id)

  def load_dataset(self):
    load_resources(u"en")
    self.engine = SnipsNLUEngine()
    with io.open(self.dataset_file) as f:
      dataset = json.load(f)
      self.engine.fit(dataset)

  def regenerate_dataset(self):
    self.log.debug("Generating snips dataset")
    files = [os.path.join(self.training_data_folder, f) for f in os.listdir(self.training_data_folder) if os.path.isfile(os.path.join(self.training_data_folder, f))]
    
    intent_files = [f for f in files if f.endswith(".int")]
    entity_files = [f for f in files if f.endswith(".ent")]
    
    
    intent_command = ""
    if len(intent_files) > 0:
      intent_command = "--intent-files"
      for intent_file in intent_files:
        intent_command += (" " + intent_file)
    
    entity_command = ""
    if len(entity_files) > 0:
      entity_command = "--entity-files"
      for entity_file in entity_files:
        entity_command += (" " + entity_file)
    
    bash_command = f"python {self.generate_dataset_file} --language en"
    if intent_command != "":
      bash_command += (" " + intent_command)
    if entity_command != "":
      bash_command += (" " + entity_command)
    
    bash_command += (" >> " + self.dataset_file)
    
    try:
      os.remove(self.dataset_file)
    except OSError:
      pass

    process = subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()

