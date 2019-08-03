# Standard imports
import json
import logging
import logging.config

# Third party imports
import flask
import sqlalchemy
import yaml

# Application imports


LOGGER = logging.getLogger(__name__)


def load_config():
    """
    Loads the config from config.yaml

    :returns: Dict of loaded config.yaml
    :rtype: dict
    """
    with open("config.yaml", "r") as _file:
        return yaml.load(_file, Loader=yaml.FullLoader)


def load_db(config):
    """
    Creates a SQLAlchemy session to be used by the controllers

    :param config: Configuration information provided by :meth:load_config
    :type config: dict
    :returns: SQLAlchemy Session
    :rtype: sqlalchemy.orm.session.Session
    """
    engine = sqlalchemy.create_engine(
        config["postgresql"]["sqlalchemy_uri"].format(**config["postgresql"])
    )
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    return Session()


def create_app():
    """
    Creates the base Flask application for running

    :returns: Flask app object
    :rtype: flask.Flask
    """
    app = flask.Flask(__name__, instance_relative_config=True)

    config = load_config()
    logging.config.dictConfig(config["logging"])
    LOGGER.debug("Logging config loaded")

    app.config.from_mapping(config)

    # Store API key for giphy client to use
    with open(config["giphy"]["api_key_location"]) as _file:
        flask.globals.giphy = {"api_key": _file.read()}

    session = load_db(config)

    # Controllers (will be moved later)
    @app.route("/")
    def default():
        """
        Default controller if someone goes to the base host not knowing to go
        to view
        :returns: Text for the user
        :rtype: str
        """
        return "Psst, go to /view instead!"

    @app.route("/login")
    def default():
        """
        Default controller if someone goes to the base host not knowing to go
        to view
        :returns: Text for the user
        :rtype: str
        """
        return "Psst, go to /view instead!"

    @app.route("/view")
    def view():
        """
        Page users can use to search from

        :returns: Rendered template
        :rtype: str
        """
        return flask.render_template("view.html")

    return app


if __name__ == "__main__":
    LOGGER.info("Application starting")
    app = create_app()
    app.run()
