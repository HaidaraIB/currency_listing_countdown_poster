import sqlalchemy as sa
from models.DB import Base
from datetime import datetime


class CurrencyListingCountdownPost(Base):
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String)
    logo = sa.Column(sa.String)
    listing_date = sa.Column(sa.DateTime)
    group_id = sa.Column(sa.Integer)
    is_posted = sa.Column(sa.Boolean, default=False)
    post_message_id = sa.Column(sa.Integer, nullable=True, default=None)

    def __str__(self):
        return (
            f"Launch Time: <b>{self.name}</b>\n\n"
            f"<b>{self.listing_date - datetime.now()}</b>"
        )
