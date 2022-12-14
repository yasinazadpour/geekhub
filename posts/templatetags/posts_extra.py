from math import ceil
from django import template
from django.utils.timesince import timesince
import markdown as md


register = template.Library()

ICONS = {
    #           dark       light
    'reddit':  ['orange', 'orange'],
    'linkedin':  ['blue', 'blue'],
    'pinterest':  ['red', 'red'],
    'github':  ['slate', 'black' ],
    'telegram':  ['blue', 'blue'],
    'facebook':  ['blue', 'blue'],
    'youtube':  ['red', 'red'],
    'twitter':  ['blue', 'blue'],
    'instagram':  ['purple', 'purple'],
    'link-45deg':  ['slate', 'black' ],
}


# tailwind color
COLORS = ["red",
    "yellow",
    "orange",
    "amber",
    "lime",
    "green",
    "emerald",
    "teal",
    "cyan",
    "sky",
    "blue",
    "indigo",
    "violet",
    "purple",
    "fuchsia",
    "pink",
    "rose",]
TUNS = [400, 500, 700, 600, 800, 300]

@register.filter("tsince", is_safe=False)
def timesince_filter(value, arg=None):
    """Format a date as the time since that date (i.e. "4 days")."""
    if not value:
        return ''
    try:
        if arg:
            return timesince(value, arg, depth=1)

        return timesince(value, depth=1)
        
    except (ValueError, TypeError):
        return ''

@register.filter("gencol")
def gen_color_filter(value):
    """genrate a color `tailwind css`"""
    if not value:
        return 'block'
    return f"{COLORS[value % 17]}-{TUNS[value % 6]}"

@register.filter("pg")
def paginator_filter(value, arg='+'):
    res = list(range(value+1, value+5))
    if arg=='-':
        res2 = list(range(value-4, value))
        return list(zip(res,res2))
    return res

@register.filter("markdown")
def markdown_filter(value):
    return md.markdown(value, extentions=['extra'])

@register.filter("readtime")
def readtime_filter(value):
    return ceil(value/200)


@register.filter("icon")
def icon_filter(value, mode='color'):
    if mode == 'color':
        return ICONS.get(value, ICONS['link-45deg'])

    elif value in ICONS.keys():
        return value
    return 'link-45deg'
