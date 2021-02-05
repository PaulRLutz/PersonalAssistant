# PersonalAssistantPython
PersonalAssistant performs commands and provides information through various, modular, plug-and-play interfaces.
Plugins contain the commands, Inputs are what take input and display output, and InteractionEngines take the input and find the necessary commands.

## Assistant.py
Assistant.py loads and manages the Plugins, Inputs, and InteractionEngines.

## Plugins
Plugins do the heavy lifting, they perform commands and get useful data.
Plugins can contain any combination of the following components:

### Helper functions
Helper functions are normal python functions that perform actions, get useful data or both.

### Command functions
Command functions use the helper functions to perform actions, and provide a human-readable output.
All Command functions start with "cmd_".

### Status
The status dictionary provides a single place for commonly-accessed information. 
It is populated with data from the helper functions.
The status dict is for quickly displaying useful information, like with the [Dashboard](https://github.com/PaulRLutz/PersonalAssistantDjangoDashboard)

## Inputs
An Input links the Assistant to the user's input. 
Inputs take text from a source, and provide a way for the InteractionEngine to get more user input, and provide the user with output.

## InteractionEngines
InteractionEngines process the user's input, prompt for more input if necessary, and provide the user the output from the command functions.
