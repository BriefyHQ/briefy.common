"""Base user type."""


class BaseUser:
    """User object with basic fields."""

    _fields = ('locale', 'fullname', 'first_name', 'last_name', 'email', 'groups')

    def __init__(self, user_id, data):
        """Initialize object from JWT token using pyramid jwt claims."""
        if not user_id:
            raise ValueError('User ID not informed.')
        self.id = user_id
        for field in self._fields:
            setattr(self, field, data.get(field))

    def to_dict(self):
        """Create a dict representation of current user.

        :return: dict serializable user data
        """
        fields = self._fields
        data = {field: getattr(self, field, None) for field in fields}
        data['id'] = self.id
        return data
