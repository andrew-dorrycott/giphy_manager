# Third party imports
import sqlalchemy

# Application imports
from models import database


class BookmarkXrefCategory(database.Base):
    __tablename__ = "bookmark_xref_categories"

    # Composite key
    bookmark_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("bookmarks.id"),
        primary_key=True,
    )
    category_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("categories.id"),
        primary_key=True,
    )

    def __init__(self, **kwargs):
        """
        Initializer

        :returns: Nothing
        :rtype: None
        """
        super(BookmarkXrefCategory, self).__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        """
        Custom String representation

        :returns: String representation of the data
        :rtype: str
        """
        message = (
            "<BookmarkXrefCategory(user_id='{user_id}', "
            + "giphy_id='{giphy_id}', category_id='{category_id}')>"
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
            "category_id": self.category_id,
        }
