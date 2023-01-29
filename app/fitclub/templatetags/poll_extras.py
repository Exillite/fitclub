from django import template

register = template.Library()

@register.filter(name='gi')
def get_item(dictionary, key):
    return dictionary.get(key)