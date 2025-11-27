import sqlalchemy as sa
from models.DB import Base
from datetime import datetime
from common.common import format_float, format_datetime


class SchedulingPost(Base):
    __tablename__ = "scheduling_posts"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    text = sa.Column(sa.String)
    photo = sa.Column(sa.String)
    doc = sa.Column(sa.String)
    interval = sa.Column(sa.Integer)
    group_id = sa.Column(sa.Integer)
    group_title = sa.Column(sa.String)

    is_paused = sa.Column(sa.Boolean, default=False)

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now)

    def __str__(self):
        return (
            "Post Scheduled:\n"
            f"Status: <b>{'Paused' if self.is_paused else 'Active'}</b>\n"
            f"Text: <b>{self.text}</b>\n"
            f"Interval: <b>{format_float(self.interval / 60)} Minutes</b>\n"
            f"Group Title: <b>{self.group_title}</b>\n"
            f"Group ID: <code>{self.group_id}</code>\n"
            f"Created At: <i>{format_datetime(self.created_at)}</i>\n"
            f"Updated At: <i>{format_datetime(self.updated_at)}</i>\n"
        )
