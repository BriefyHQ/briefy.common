"""Common Colander validators used on Briefy."""
from briefy.common import _
import colander

EventName = colander.Regex(r'^(([a-z])+\.([a-z])+)+$', _('Invalid event name'))
