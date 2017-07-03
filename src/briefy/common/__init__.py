"""Briefy Common."""
import translationstring


_ = translationstring.TranslationStringFactory(__name__)


def init():
    """Initialize things that need initializing on import."""
    from briefy.common.utils import json_override

    json_override.init()


init()
