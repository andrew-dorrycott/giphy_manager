# Third party imports
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, nullable=False
    )
    username = sqlalchemy.Column(
        sqlalchemy.String, unique=True, nullable=False
    )
    # Needs to be encrypted
    password = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    def __init__(self, **kwargs):
        """
        Initalizer

        :returns: Nothing
        :rtype: None
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        """
        Custom String representation

        :returns: String representation of the data
        :rtype: str
        """
        return "<User(id='{id}', username='{username}')>".format(
            **self.__dict__
        )

    def to_dict(self):
        """
        Custom Dictionary/Json-able representation

        :returns: Dict representation of the data
        :rtype: dict
        """
        return {"id": self.id, "username": self.username}
