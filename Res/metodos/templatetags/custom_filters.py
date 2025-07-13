import json
from django import template

register = template.Library()


@register.filter(name="json_load")
def json_load(value):
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return value
