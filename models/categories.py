# Third party imports
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Category(Base):
    __tablename__ = "categories"

    # Composite key
    name = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    user_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), primary_key=True
    )

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
