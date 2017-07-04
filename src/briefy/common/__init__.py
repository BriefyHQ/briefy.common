"""Briefy Common."""
import translationstring


_ = translationstring.TranslationStringFactory(__name__)


def init():
    """Initialize things that need initializing on import."""
    from briefy.common.utils import json_override
    from sqlalchemy_continuum import make_versioned

    json_override.init()
    make_versioned()


init()
