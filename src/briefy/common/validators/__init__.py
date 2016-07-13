"""Common Colander validators used on Briefy."""
from briefy.common import _
import colander

EventName = colander.Regex(r'^(([a-z])+\.([a-z])+)+$', _('Invalid event name'))


def empty_or(external_validator):
    def validator(request, data):
        if data:
            return external_validator(request, data)
        return None
