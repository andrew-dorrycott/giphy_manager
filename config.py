# Third Party imports
import yaml


def load_config():
    """
    Loads the config from config.yaml and inserts the giphy api_key into config

    :returns: Dict of loaded config.yaml
    :rtype: dict
    """
    with open("config.yaml", "r") as _file:
        config = yaml.load(_file, Loader=yaml.FullLoader)

    with open(config["giphy"]["api_key_location"]) as _file:
        config["giphy"]["api_key"] = _file.read()

    return config


# Push loaded config.yaml into globals for quick access to the rest of the app
config_globals = globals()
config_globals.update(load_config())
