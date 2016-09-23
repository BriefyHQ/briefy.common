"""Base user type."""


class BaseUser:
    """Class to represent the user interface.
    """
    _fields = ('locale', 'fullname', 'first_name', 'last_name', 'email', 'groups')

    def __init__(self, user_id, data):
        """Initialize object from JWT token using pyramid jwt claims."""
        self.id = user_id
        for field in self._fields:
            setattr(self, field, data.get(field))

    def to_dict(self):
        """Create a dict representation of current user.

        :return: dict serializable user data
        """
        fields = self._fields
        fields.append('id')
        return {field: getattr(self, field, None) for field in self._fields}
