# Third party imports
import sqlalchemy

# Application imports
from models import database


class Bookmark(database.Base):
    __tablename__ = "bookmarks"

    # Due to the complexities of Composite Foreign keys in SQLAlchemy a
    # traditional single id primary_key column will be used
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    user_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id")
    )
    giphy_id = sqlalchemy.Column(sqlalchemy.String)
    user = sqlalchemy.orm.relationship("User", back_populates="bookmarks")
    favorite = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    categories = sqlalchemy.orm.relationship(
        "Category", secondary="bookmark_xref_categories"
    )

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
        message = (
            "<BookMark(id='{user_id}', giphy_id='{giphy_id}', "
            + "favorite='{favorite}')>"
        )
        return message.format(**self.__dict__)

    def to_dict(self):
        """
        Custom Dictionary/Json-able representation

        :returns: Dict representation of the data
        :rtype: dict
        """
        return {
            "user_id": self.user_id,
            "giphy_id": self.giphy_id,
            "favorite": self.favorite,
        }
