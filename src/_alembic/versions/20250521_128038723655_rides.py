"""rides

Revision ID: 128038723655
Revises: 2030fbc3fe48
Create Date: 2025-05-21 17:54:36.648570

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '128038723655'
down_revision: Union[str, None] = '2030fbc3fe48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rides',
    sa.Column('city_id_departure', sa.Uuid(), nullable=False),
    sa.Column('city_id_destination', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('departure_time', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('is_cancelled', sa.Boolean(), nullable=False),
    sa.Column('owner_id', sa.Uuid(), nullable=False),
    sa.Column('price_currency', sa.Enum('DKK_ORE', 'EUR_CENT', 'GBP_PENCE', 'PLN_GROSZ', 'RUB_KOPECK', name='currency'), nullable=False),
    sa.Column('price_value', sa.Integer(), nullable=False),
    sa.Column('seats_available', sa.SmallInteger(), nullable=False),
    sa.Column('seats_number', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ride_city_from_to_departure', 'rides', ['city_id_departure', 'city_id_destination', 'departure_time'], unique=False)
    op.create_index(op.f('ix_rides_id'), 'rides', ['id'], unique=False)
    op.create_table('passengers',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('ride_id', sa.Uuid(), nullable=False),
    sa.Column('seats_booked', sa.SmallInteger(), nullable=False),
    sa.ForeignKeyConstraint(['ride_id'], ['rides.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', 'ride_id')
    )
    op.create_index(op.f('ix_passengers_id'), 'passengers', ['id'], unique=False)
    op.create_index(op.f('ix_passengers_ride_id'), 'passengers', ['ride_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_passengers_ride_id'), table_name='passengers')
    op.drop_index(op.f('ix_passengers_id'), table_name='passengers')
    op.drop_table('passengers')
    op.drop_index(op.f('ix_rides_id'), table_name='rides')
    op.drop_index('ix_ride_city_from_to_departure', table_name='rides')
    op.drop_table('rides')
    sa.Enum(name='currency').drop(op.get_bind())
    # ### end Alembic commands ###