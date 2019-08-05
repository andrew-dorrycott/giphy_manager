# Standard imports
import logging
import logging.config

# Third party imports
import flask

# Application imports
from models import database
import config
from controllers.controllers import base


LOGGER = logging.getLogger(__name__)


def create_app():
    """
    Creates the base Flask application for running

    :returns: Flask app object
    :rtype: flask.Flask
    """
    app = flask.Flask(__name__, instance_relative_config=True)
    app.register_blueprint(base)

    # Load logging
    logging.config.dictConfig(config.logging)
    LOGGER.debug("Logging config loaded")

    # Load configs
    with open(config.giphy["api_key_location"]) as _file:
        config.giphy["api_key"] = _file.read()
    app.config.from_object(config)

    # Load database
    database.init_db()

    return app


if __name__ == "__main__":
    LOGGER.info("Application starting")
    app = create_app()
    app.run()
