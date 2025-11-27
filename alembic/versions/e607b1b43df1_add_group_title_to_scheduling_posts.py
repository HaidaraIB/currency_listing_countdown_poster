"""add group_title to scheduling_posts

Revision ID: e607b1b43df1
Revises: 910d5fb2adf8
Create Date: 2025-11-27 13:54:34.874990

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e607b1b43df1"
down_revision: Union[str, None] = "910d5fb2adf8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    try:
        with op.batch_alter_table("scheduling_posts") as batch_op:
            batch_op.add_column(
                sa.Column(
                    "group_title",
                    sa.String,
                    nullable=True,
                    default=None,
                )
            )
    except:
        pass


def downgrade() -> None:
    pass
