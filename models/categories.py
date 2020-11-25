# Third party imports
import sqlalchemy

# Application imports
from models import database


class Category(database.Base):
    __tablename__ = "categories"

    # Due to the complexities of Composite Foreign keys in SQLAlchemy a
    # traditional single id primary_key column will be used
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    user_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id")
    )
    user = sqlalchemy.orm.relationship("User", back_populates="categories")

    def __init__(self, **kwargs):
        """
        Initalizer

        :returns: Nothing
        :rtype: None
        """
        super(Category, self).__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        """
        Custom String representation

        :returns: String representation of the data
        :rtype: str
        """
        return "<Category(user='{user}', name='{name}')>".format(
            **self.__dict__
        )

    def to_dict(self):
        """
        Custom Dictionary/Json-able representation

        :returns: Dict representation of the data
        :rtype: dict
        """
        return {"id": self.id, "name": self.name}
