import os
from ayon_core.addon import (
    AYONAddon
)
from .version import __version__

MY_STUDIO_ADDON_ROOT = os.path.dirname(os.path.abspath(__file__))
ADDON_NAME = "jean_moulinette"
ADDON_LABEL = "JeanMoulinette"

class JeanMoulinette(AYONAddon):
    name = ADDON_NAME
    label = ADDON_LABEL
    version = __version__

    def initialize(self, settings):
        """Initialization of module."""
        
        pass
