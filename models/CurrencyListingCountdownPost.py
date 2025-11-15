import sqlalchemy as sa
from models.DB import Base
from datetime import datetime


class CurrencyListingCountdownPost(Base):
    __tablename__ = "currency_listing_countdown_posts"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String)
    logo = sa.Column(sa.String)
    listing_date = sa.Column(sa.DateTime)
    group_id = sa.Column(sa.Integer)
    is_posted = sa.Column(sa.Boolean, default=False)
    post_message_id = sa.Column(sa.Integer, nullable=True, default=None)

    def __str__(self):
        return (
            f"Launch Time: <b>{self.name}</b>\n\n" f"<b>{self.get_time_remaining()}</b>"
        )

    def get_time_remaining(self) -> str:
        total_seconds = int((self.listing_date - datetime.now()).total_seconds())
        if total_seconds < 0:
            return "تم الإطلاق"
        days = total_seconds // (24 * 3600)
        hours = (total_seconds % (24 * 3600)) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{days:02}:{hours:02}:{minutes:02}:{seconds:02}"
