"""add is_pinned field to CurrencyListingCountdownPost table

Revision ID: 910d5fb2adf8
Revises:
Create Date: 2025-11-20 16:51:30.406711

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "910d5fb2adf8"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    try:
        with op.batch_alter_table("currency_listing_countdown_posts") as batch_op:
            batch_op.add_column(
                sa.Column(
                    "is_pinned",
                    sa.Boolean,
                    default=False,
                )
            )
    except:
        pass


def downgrade() -> None:
    try:
        with op.batch_alter_table("currency_listing_countdown_posts") as batch_op:
            batch_op.drop_column("is_pinned")
    except:
        pass
