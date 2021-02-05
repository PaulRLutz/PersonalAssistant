"""
  simple explanation for translating enum to Django "choices": https://stackoverflow.com/questions/54802616/how-to-use-enums-as-a-choice-field-in-django-model

  Possible extra comparison operators (like "IN" in a datetime range): https://docs.oracle.com/cd/B12037_01/olap.101/b10339/datatypes002.htm#g1026096

  Making sure at least field is active with "clean": https://stackoverflow.com/questions/53085645/django-one-of-2-fields-must-not-be-null
"""

# TODO: 

from enum import Enum
from django.db import models
from django.core.validators import int_list_validator
from .validators import validate_actions_json_list

class ComparisonOperator(Enum):
  EQ = "EQ" #"equal"
  NE = "NE" #"not_equal"
  GT = "GT" #"greater_than"
  LT = "LT" #"less_than"
  GE = "GE" #"greater_than_or_equal"
  LE = "LE" #"less_than_or_equal"

  @classmethod
  def choices(cls):
    print(tuple((i.name, i.value) for i in cls))
    return tuple((i.name, i.value) for i in cls)

class LogicalOperator(Enum):
  OR = "OR"
  AND = "AND"

  @classmethod
  def choices(cls):
    print(tuple((i.name, i.value) for i in cls))
    return tuple((i.name, i.value) for i in cls)

"""
  Plugin variable contains the plugin name, and the variable name.
  Each plugin must register its own avaiable variables, and PluginVariables must come from that compiled list
"""
# TODO 'clean' function to very registered variable
class PluginVariable(models.Model):
  plugin_name = models.CharField(max_length=200)
  variable_name = models.CharField(max_length=200)

"""
  A BooleanExpression consists of a PluginVariable, a ComparisonOperator, and either another PluginVariable, OR a constant (not both)
  A BooleanExpression is checked when PluginVariable 'A' is changed. The ComparisonOperator is then used to compare it to the "Value B"
  The result of the BooleanExpression is handled by the ConditionalStatement
"""
class BooleanExpression(models.Model):
  plugin_variable_a = models.ForeignKey(PluginVariable, related_name="plugin_variable_a", on_delete=models.CASCADE)

  comparison_operator = models.CharField(max_length=2,choices=ComparisonOperator.choices())

  plugin_variable_b = models.ForeignKey(PluginVariable, related_name="plugin_variable_b", on_delete=models.CASCADE)
  constant_b = models.CharField(max_length=200)

  def clean(self):
    super().clean()
    if self.plugin_variable_a is not None and self.constant_b is not None:
      raise ValidationError("Only one of the 'Value B' values can be used")

# TODO: Django 'clean' function to make sure the ConditionalStatement is valid
# TODO 'action' or 'reset' must be null
class ConditionalStatement(models.Model):
  active = models.BooleanField(default=True)

  boolean_expressions = models.ManyToManyField(BooleanExpression)
  boolean_expressions_positions = models.CharField(validators=[int_list_validator], max_length=200)

  logical_operators = models.CharField(validators=[validate_actions_json_list], max_length=2000, default="[]")
  logical_operators_positions = models.CharField(validators=[int_list_validator], max_length=200, default="[]")

  open_paren_positions = models.CharField(validators=[int_list_validator], max_length=100)
  close_paren_positions = models.CharField(validators=[int_list_validator], max_length=100)

  actions_json_list = models.CharField(max_length=2000, default="[]", validators=[validate_actions_json_list])
