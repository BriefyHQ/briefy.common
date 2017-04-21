"""Common Colander validators used on Briefy."""
from briefy.common import _

import colander


EventName = colander.Regex(r'^(([a-z_])+\.([a-z_0-9])+)+$', _('Invalid event name'))


def empty_or(external_validator):
    """Implement a validator that is either empty or delegates to another validator.

    :param external_validator: A validator to be chained if there is data.
    """
    def validator(request, data):
        """Validator method.

        :param request: Request.
        :param data: Data to be validated.
        """
        if data:
            return external_validator(request, data)
        return None
