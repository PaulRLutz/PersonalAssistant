from django.core.exceptions import ValidationError
import json

"""
raise ValidationError(
            _('%(value)s is not an even number'),
            params={'value': value},
        )
"""
# TODO: validate json "list", input possible values, raise error if list has values that aren't specified
"""
  First step in validating an object stored as a json list
  Returns: 
    json_list: the list pulled from the json string
  Raises:
    ValueError: ValidationError, if the string is not a valid json string, or if it doesn't hold a list
"""
def get_json_list(value):
  try:
    json_object = json.loads(value)
    if isinstance(json_object, list):
      return json_list
    else:
      raise ValidationError("JSON object must be a string",)
  except ValueError:
    raise ValidationError("Not a valid JSON object",)

def validate_actions_json_list(value):
  json_list = get_json_list(value)

def validate_logical_operators_list(l):
  json_list = get_json_list(value)
