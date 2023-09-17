from django import template

register = template.Library()

@register.filter
def clear_space(value):
    return str(value).replace(' ', '')