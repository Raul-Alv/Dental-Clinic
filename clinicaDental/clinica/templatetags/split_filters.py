from django import template

register = template.Library()

@register.filter(name='split')
def split(value, sep):
    if not isinstance(value, str):
        return value
    return value.split(sep)