from django.contrib import admin

from .models import PluginVariable, BooleanExpression, ConditionalStatement

admin.site.register(PluginVariable)
admin.site.register(BooleanExpression)
admin.site.register(ConditionalStatement)
