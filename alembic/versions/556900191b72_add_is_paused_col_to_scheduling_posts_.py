"""add is_paused col to scheduling_posts table

Revision ID: 556900191b72
Revises: e607b1b43df1
Create Date: 2025-11-27 22:47:20.074087

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "556900191b72"
down_revision: Union[str, None] = "e607b1b43df1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    try:
        with op.batch_alter_table("scheduling_posts") as batch_op:
            batch_op.add_column(
                sa.Column(
                    "is_paused",
                    sa.Boolean,
                    default=False,
                )
            )
    except:
        pass


def downgrade() -> None:
    try:
        with op.batch_alter_table("scheduling_posts") as batch_op:
            batch_op.drop_column("is_paused")
    except:
        pass
