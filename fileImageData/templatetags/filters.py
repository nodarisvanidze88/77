# your_app/templatetags/filters.py
import os
from django import template

register = template.Library()

@register.filter
def basename(value):
    """
    Return the final component of a pathname
    e.g. /tmp/myfile.txt -> myfile.txt
    """
    return os.path.basename(value)
