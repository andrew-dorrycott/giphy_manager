# Third party imports
import sqlalchemy

# Application imports
from models import database


class Bookmark(database.Base):
    __tablename__ = "bookmarks"

    # Composite key
    user_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), primary_key=True
    )
    user = sqlalchemy.orm.relationship("User", back_populates="bookmarks")
    giphy_id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    favorite = sqlalchemy.Column(sqlalchemy.Boolean)

    def __init__(self, **kwargs):
        """
        Initializer

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
        return "<BookMark(id='{id}', description='{description}')>".format(
            **self.__dict__
        )

    def to_dict(self):
        """
        Custom Dictionary/Json-able representation

        :returns: Dict representation of the data
        :rtype: dict
        """
        return {
            "user_id": self.user_id,
            "giphy_id": self.giphy_id,
            "favorite": self.favorite
        }
