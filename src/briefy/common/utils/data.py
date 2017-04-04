"""Helpers to deal with simple data."""
from slugify import slugify
from uuid import uuid4

import inspect


def generate_uuid() -> str:
    """Generate an uuid4.

    :returns: A UUID4 string
    """
    return str(uuid4())


def generate_slug(value: str) -> str:
    """Given a value, return the slugified version of it.

    :param value: A string to be converted to a slug
    :return: A url-friendly slug of a value.
    """
    return slugify(value)


def generate_contextual_slug(context: dict) -> str:
    """Given a context, calculate the slug for it.

    :param context: Dictionary containing some values like id and title.
    :return: A url-friendly slug of a value.
    """
    if not isinstance(context, dict):
        context = context.current_parameters

    obj_id = context.get('id', '')
    title = context.get('title', '')

    slug_id = str(obj_id)[:8] if obj_id else ''
    slug_title = generate_slug(title) if title else ''

    if slug_id and slug_title:
        slug = '{slug_id}-{slug_title}'.format(
            slug_id=slug_id,
            slug_title=slug_title
        )
    else:
        slug = slug_id if slug_id else slug_title
    return slug


objectify_sentinel = object()


class Objectify:
    """Alows using values of nested JSON-like data structures as Python objects.

    Helper class to make SQS and HTTP payloads easy to use without
    going too full model declaration. Works great for JSON and
    JSON like objects - avoiding a lot of extraneous
    brackets and quotes for attribute access.

    This works by wrapping a Dictionary or List in Python with
    a  `__getattr__` call, which recursively builds more objects
    of this class if attributes retrieved are also dict or lists.

    List members work as attributes with a `_` prepending their index number.

    If the data structure is needed at any point, it is always available
    from an empty call to _get

    The `_get` method works as a dictionary get but allows for a dot
    separated attribute path.

    The `_traverse` and `_get_traverser` methods allow retrieving
    attributes from a relative path retrieved from two or more root-paths
    in an hierarchical order,

    Normally, on trying to retrieve any non-existing attribute, one will get
    an AttributeError - although setting the instance "_sentinel" attribute
    to any object, will return that object on attribute access error instead.

    """

    def __init__(self, dct: (dict, list), sentinel=objectify_sentinel):
        """Initalizer.

        :param dct: Container JSON-Like object to be used.
        """
        # DEPRECATED: Remove '.dct' and leave '._dct' as soon
        # as there are no other references to '.dct' on users of this helper.
        if isinstance(dct, Objectify):
            dct = dct._dct
        self._dct = self.dct = dct
        self._sentinel = sentinel

    def _acceptable_attr(self, attr):
        # DEPRECATED: Remove 'dct' from next verification soon.
        if attr == 'dct' or (attr.startswith('_') and not attr.strip('_').isdigit()):
            return False
        return True

    def _normalize_attr(self, attr):
        """Allow use of numbers prefixed by underscores as attributes when the object is a list."""
        if attr.isdigit():
            return int(attr)
        if attr.startswith("_") and attr.strip('_').isdigit():
            attr = int(attr[1:].replace('_', '-'))
        return attr

    def __getitem__(self, attr):
        """Retrieve attribute from data container.

        If the retrieved value is itself a container, wrap it
        into an "Objectify" instance.
        """
        result = self._dct.__getitem__(attr)
        if isinstance(result, (dict, list)):
            return Objectify(result, self._sentinel)
        return result

    def __getattr__(self, attr):
        """Retrieve attribute from underliying object."""
        attr = self._normalize_attr(attr)
        try:
            return self.__getitem__(attr)
        except (KeyError, IndexError, TypeError) as error:
            if self._sentinel is not objectify_sentinel:
                return self._sentinel
            raise AttributeError from error

    def __setattr__(self, attr, value):
        """Set apropriate attribute on underlying object."""
        if not self._acceptable_attr(attr):
            return super().__setattr__(attr, value)
        attr = self._normalize_attr(attr)
        try:
            self.__setitem__(attr, value)
        except IndexError as error:
            raise AttributeError from error

    def __setitem__(self, attr, value):
        """Set apropriate attribute on data container."""
        self._dct.__setitem__(attr, value)

    def __iter__(self):
        """Allow one to iterate over the members of this object.

        Note that this by itself makes these objects  better than Javascript
        objects due to iterating over data members, and no need to check "hasOwnProperty".

        """
        items = self._dct if isinstance(self._dct, list) else self._dct.values()
        for item in items:
            yield Objectify(item, self._sentinel) if isinstance(item, (dict, list)) else item

    def __dir__(self):
        """Dir: enables autocomplete."""
        keys = (
            list(self._dct.keys())
            if isinstance(self._dct, dict) else
            ['_{0}'.format(index) for index in range(len(self._dct))]
        )
        return ['_dct', '_sentinel'] + keys

    def __repr__(self):
        """Representation."""
        return('Objectify({})'.format(self.dct))

    def __bool__(self):
        """Assure truthy value is False when appropriate."""
        return bool(self.dct)

    def _get(self,
             path: str=None,
             default: 'any'=objectify_sentinel,
             objectify: bool=objectify_sentinel)-> "any":
        """Retrieve an attribute at an arbitrarily deep path.

        This is a public method. "_" is used to avoid clash with data keys.
        Paths should be a dot separated string, just as if
        Python object atrribute access was being done. Paths that
        traverse list components may or not prefix the index_list with
        a "_".

        :param path: path
        :param default: default value if attribute can't be reached.
                        if not passed, returns self._sentinel if set
                        to anything else than 'objectify_sentinel", else raises AttributeError.
        :param objectify: If false, a final attribute that is a list or dict
                          will be returned raw, and not objectified.
        """
        dct = self._dct
        if path is None:
            if not objectify or objectify is objectify_sentinel:
                return dct
            return self
        try:
            for component in path.split('.'):
                if not component:
                    continue
                dct = dct[self._normalize_attr(component)]
        except (KeyError, IndexError, TypeError) as error:
            if default is not objectify_sentinel:
                return default
            raise AttributeError from error

        if objectify and isinstance(dct, (dict, list)):
            return Objectify(dct, self._sentinel)
        return dct

    def _traverse(self,
                  roots: list,
                  branch: str,
                  default: 'any'=objectify_sentinel,
                  objectify: bool=True)-> 'any':
        """Retrieve attribute from one of various sub-structures withn main struct.

        Prefer to use ._get_traverser instead.

        :param roots: list of paths as strings from which to try to retrieve 'branch' attribute
        :param branch: path relative to roots where attribute will be sought
        :param default: what to return if attribut is not find in any root.
                        Raises AttributeError by default.
        :param objectify: Whether to return an Objetify wrapper if
                          retrieved attribute is a list or dict,
        :return: retrieved attribute.
        """
        for path in roots:
            try:
                value = self._get('.'.join((path, branch)), objectify=objectify)
            except AttributeError:
                continue
            else:
                return value
        if default is objectify_sentinel:
            raise AttributeError
        return default

    def _get_traverser(
            self,
            roots: list,
            default: 'any' = objectify_sentinel) -> 'any':
        """Return a "traverser" able to retrieve relative attributes starting from multiple paths.

        Prefer this to ._traverse above.

        Justificative: within many configuration parameters we have subsets of
        parameters that override those present in another place in the same
        JSON structure. For example, an Assignment will be linked
        to an Order and a Project. If the Order has any "tech_requirements"
        those should superceed the tech_requirements for the Project.

        Another example: Delivery configuration for projects can have configurations for
        "Archiving" and "Delivery" - but most fields will be the same for both
        configurations, but for one or two ('parent_folder', for example).
        Traversal allows a "deliver_requirements' section to hold all common fields
        (like renaming operations, resizing, and such) while differing fields
        are each retrived from its own section.

        Example:
        data = {'order': {'requirements': {'width': 640}},
                'project': {'requirements': {'height': 480}},
                'requirements': {'duration': '10s'}
                }
        obj = Objectify(data)._get_traverser([
                'requirements', 'order.requirements', 'project.requirements'])
        obj('width') -> 640
        obj('height') -> 480
        obj('duration') -> '10s'

        :param roots: list of paths as strings from which to try to retrieve 'branch' attribute
        :param default: what to return if attribut is not find in any root.
                        Raises AttributeError by default.
        :return: retrieved attribute.
        """
        return _Traverser(self, roots, default)


class _Traverser:
    """Helper class used by Objectify.

    Should not be instantiated directly - use Objectify(...)._get_traverser(...)
    """

    def __init__(self, obj: Objectify, roots: list, default, branch=None):
        """Keep configuration attributes."""
        self._obj = obj
        self._roots = roots
        self._default = default
        self._branch = branch if branch else []

    def __getattr__(self, attr):
        """Perform a search in the configured root paths on the parent object.

        Returns a new instance of _Traverser if the retrieved attribute is
        an Objectify instance - so that the search can proceed from the
        walked path so far.
        """
        result = self(attr)
        if isinstance(result, Objectify):
            return _Traverser(self._obj, self._roots, self._default, self._branch + [attr])
        return result

    def __call__(self, path: str, objectify=True):
        """Perform a single search on given path under all configured roots.

        Path can be a dotted path to an attribute. The resulting object
        is either an Objectify instance, or its raw data structure -
        and can no longer perform traversal.
        """
        return self._obj._traverse(
            self._roots,
            '.'.join(self._branch + [path]),
            default=self._default,
            objectify=True
        )


def _accepts_pos_kw(func=None, signature=None):
    """Return a boolean 2-tuple on whether a function accepts *args or **kw."""
    signature = signature or inspect.signature(func)
    parameter_types = {p.kind for p in signature.parameters.values()}
    return (inspect.Parameter.VAR_POSITIONAL in parameter_types,
            inspect.Parameter.VAR_KEYWORD in parameter_types)


def inject_call(func: 'callable', *args: ['any'], **kwargs: {str: 'any'}) -> 'any':
    """Perform a function call, injecting apropriate parameters from kwargs.

    Other parameters are ignored.  (If you want errors on nonexisting parameters
    just call the function directly)

    :param func: the callable
    :param args: positional args to be unconditionally forwarded to the callable
    :param kwargs: keyword parameters that will be filtered to whatever the callable
                   explicitly accepts before being forwarded.
    :return: Whatever the callale returns.
    """
    signature = inspect.signature(func)

    accepts_pos, accepts_kw = _accepts_pos_kw(signature=signature)
    if accepts_kw:
        # Anything goes -
        return func(*args, **kwargs)

    new_kw = {}
    for key, value in kwargs.items():
        if key in signature.parameters:
            new_kw[key] = value
    return func(*args, **new_kw)
