"""Local development settings. DEBUG is opt-in through the environment."""

from .base import *  # noqa: F403

DEBUG = env_bool("DEBUG", False)  # noqa: F405
