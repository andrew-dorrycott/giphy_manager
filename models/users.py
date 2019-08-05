# Third party imports
import sqlalchemy

# Application imports
from models import database


class User(database.Base):
    __tablename__ = "users"

    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, nullable=False
    )
    username = sqlalchemy.Column(
        sqlalchemy.String, unique=True, nullable=False
    )
    # Needs to be encrypted
    password = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    # For simplicity sake, the users token will be saved to their user record
    # In Enterprise software, this belongs in memcached, Redis, or some other
    # Cache system
    token = sqlalchemy.Column(sqlalchemy.String)

    # Relationships
    categories = sqlalchemy.orm.relationship("Category", back_populates="user")
    bookmarks = sqlalchemy.orm.relationship("Bookmark", back_populates="user")

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
        return {
            "id": self.id,
            "username": self.username,
            "categories": self.categories,
        }
