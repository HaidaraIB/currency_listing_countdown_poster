"""add gif col to scheduling_posts table

Revision ID: 26f52ebeac44
Revises: 556900191b72
Create Date: 2025-11-27 23:09:29.364675

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '26f52ebeac44'
down_revision: Union[str, None] = '556900191b72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    try:
        with op.batch_alter_table("scheduling_posts") as batch_op:
            batch_op.add_column(
                sa.Column(
                    "gif",
                    sa.String,
                    nullable=True,
                    default=None,
                )
            )
    except:
        pass


def downgrade() -> None:
        try:
            with op.batch_alter_table("scheduling_posts") as batch_op:
                batch_op.drop_column("gif")
        except:
            pass
