"""Briefy Common."""
import translationstring


_ = translationstring.TranslationStringFactory(__name__)


def init():
    """Initialize things that need initializing on import."""
    from briefy.common.utils import json_override
    from sqlalchemy_continuum import make_versioned

    json_override.init()
    # As our users are not in here, it is not easy to keep track
    # of changes using this
    make_versioned(user_cls=None)


init()
