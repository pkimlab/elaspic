import os
import six
import logging

from . import conf

logger = logging.getLogger(__name__)
configs = conf.CONFIGS

ELASPIC_LOGO = """

8888888888 888             d8888  .d8888b.  8888888b. 8888888 .d8888b.
888        888            d88888 d88P  Y88b 888   Y88b  888  d88P  Y88b
888        888           d88P888 Y88b.      888    888  888  888    888
8888888    888          d88P 888  "Y888b.   888   d88P  888  888
888        888         d88P  888     "Y88b. 8888888P"   888  888
888        888        d88P   888       "888 888         888  888    888
888        888       d8888888888 Y88b  d88P 888         888  Y88b  d88P
8888888888 88888888 d88P     888  "Y8888P"  888       8888888 "Y8888P"

"""


# %%
class Pipeline:

    def __init__(self, configurations):
        """.

        It should be possible to initialize one pipeline and call it in parallel using different
        mutations as input.
        """
        # Read the configuration file and set the variables
        if isinstance(configurations, six.string_types):
            conf.read_configuration_file(configurations)
        elif isinstance(configurations, dict):
            configs.update(**configurations)

        # Initialize a logger
        for line in ELASPIC_LOGO.split('\n'):
            logger.info(line)

        self.PWD = os.getcwd()

        # Each one leads to the next...
        self.seqrecords = []
        self.sequences = {}
        self.models = {}
        self.predictions = {}


_instances = {}


def execute_and_remember(f):
    """A basic memoizer."""
    def f_new(*args, **kwargs):
        key = tuple([f] + list(args))
        if key in _instances:
            return _instances[key].result

        else:
            instance = f(*args, **kwargs)
            if instance:
                with instance:
                    instance.run()
            _instances[key] = instance
            return _instances[key].result

    return f_new
