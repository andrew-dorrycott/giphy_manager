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


# Push loaded config.yaml into globals for quick access to the rest of the app
config_globals = globals()
config_globals.update(load_config())
