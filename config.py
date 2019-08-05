# Third Party imports
import yaml


def load_config():
    """
    Loads the config from config.yaml

    :returns: Dict of loaded config.yaml
    :rtype: dict
    """
    with open("config.yaml", "r") as _file:
        return yaml.load(_file, Loader=yaml.FullLoader)


# Magic, this is going to look kinda bad
# This right here is extremely bad practice :D
config_globals = globals()
config_globals.update(load_config())
