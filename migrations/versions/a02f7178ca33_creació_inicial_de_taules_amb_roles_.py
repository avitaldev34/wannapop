"""Creació inicial de taules amb roles, categories i claus foranes

Revision ID: a02f7178ca33
Revises: 
Create Date: 2025-11-23 23:13:52.900262

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a02f7178ca33'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Ja no creem categories ni roles perquè ja existeixen

    # Alterar taula products
    with op.batch_alter_table('products', schema=None) as batch_op:
        # Afegim category_id com nullable per evitar errors amb dades existents
        batch_op.add_column(sa.Column('category_id', sa.Integer(), nullable=True))
        batch_op.alter_column('description',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               existing_nullable=False)
        batch_op.alter_column('price',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               type_=sa.Float(),
               existing_nullable=False)
        # seller_id també es deixa nullable per evitar errors amb dades existents
        batch_op.alter_column('seller_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.create_foreign_key(
            'fk_products_category', 'categories', ['category_id'], ['id']
        )
        batch_op.create_foreign_key(
            'fk_products_seller', 'users', ['seller_id'], ['id']
        )
        batch_op.drop_column('updated')
        batch_op.drop_column('created')

    # Alterar taula users
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_users_role', 'roles', ['role_id'], ['id']
        )
        batch_op.drop_column('updated')
        batch_op.drop_column('created')


def downgrade():
    # Revertir taula users
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created', sa.DATETIME(), nullable=True))
        batch_op.add_column(sa.Column('updated', sa.DATETIME(), nullable=True))
        batch_op.drop_constraint('fk_users_role', type_='foreignkey')
        batch_op.drop_column('role_id')

    # Revertir taula products
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created', sa.DATETIME(), nullable=True))
        batch_op.add_column(sa.Column('updated', sa.DATETIME(), nullable=True))
        batch_op.drop_constraint('fk_products_category', type_='foreignkey')
        batch_op.drop_constraint('fk_products_seller', type_='foreignkey')
        batch_op.alter_column('seller_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('price',
               existing_type=sa.Float(),
               type_=sa.NUMERIC(precision=10, scale=2),
               existing_nullable=False)
        batch_op.alter_column('description',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               existing_nullable=False)
        batch_op.drop_column('category_id')

    # Ja no eliminem categories ni roles perquè ja existeixen
