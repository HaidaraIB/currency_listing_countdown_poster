import sqlalchemy as sa
from models.DB import Base
from datetime import datetime


class SchedulingPost(Base):
    __tablename__ = "scheduling_posts"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    text = sa.Column(sa.String)
    photo = sa.Column(sa.String)
    interval = sa.Column(sa.Integer)
    group_id = sa.Column(sa.Integer)

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now)

    def __str__(self):
        return (
            "Post Scheduled:\n"
            f"Text: <b>{self.text}</b>\n"
            f"Interval: <b>{self.interval} Minutes</b>\n"
            f"Group ID: <code>{self.group_id}</code>\n"
            f"Created At: <i>{self.created_at}</i>\n"
            f"Updated At: <i>{self.updated_at}</i>\n"
        )
