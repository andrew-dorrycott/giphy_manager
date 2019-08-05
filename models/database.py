# Third party imports
import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


##
# For those watching, thank you for hanging out while I pound through this <3's
# There skipped that song, fuck it anyways
##


# Copied for now
def load_config():
    """
    Loads the config from config.yaml

    :returns: Dict of loaded config.yaml
    :rtype: dict
    """
    import yaml
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


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()

    # Prevent circular imports
    from models import categories  # noqa: F401
    from models import bookmarks  # noqa: F401
    from models import users  # noqa: F401

    Base.metadata.create_all(bind=engine)


config = load_config()
engine = sqlalchemy.create_engine(
    config["postgresql"]["sqlalchemy_uri"].format(**config["postgresql"])
)
session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()
Base.query = session.query_property()
