# Third party imports
from cryptography.fernet import Fernet
from sqlalchemy.ext.hybrid import Comparator
from sqlalchemy.ext.hybrid import hybrid_property
import sqlalchemy

# Application imports
from models import database
import config


class User(database.Base):
    __tablename__ = "users"

    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, nullable=False
    )
    username = sqlalchemy.Column(
        sqlalchemy.String, unique=True, nullable=False
    )
    # Needs to be encrypted
    enc_password = sqlalchemy.Column(sqlalchemy.LargeBinary, nullable=False)

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

    @hybrid_property
    def password(self):
        cipher = Fernet(config.postgresql["salt"])
        return cipher.decrypt(self.enc_password)

    # Not working as intended right now
    # class encrypt_comparator(Comparator):
    #     def __init__(self, enc_password):
    #         self.enc_password = enc_password

    #     def __eq__(self, other):
    #         cipher = Fernet(config.postgresql["salt"])
    #         return self.enc_password == cipher.encrypt(str.encode(other))

    # @password.comparator
    # def password(cls):
    #     return User.encrypt_comparator(cls.enc_password)

    @password.setter
    def password(self, value):
        cipher = Fernet(config.postgresql["salt"])
        self.enc_password = cipher.encrypt(str.encode(value))

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
