"""add currencies, countries and backtests tables

Revision ID: 004
Revises: 003
Create Date: 2025-01-04 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Create currencies table
    op.create_table(
        'currencies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=3), nullable=False),
        sa.Column('numeric_code', sa.String(length=3), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('name_en', sa.String(length=100), nullable=True),
        sa.Column('symbol', sa.String(length=10), nullable=True),
        sa.Column('decimal_places', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('is_active', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_currencies_id', 'currencies', ['id'])
    op.create_index('ix_currencies_code', 'currencies', ['code'], unique=True)

    # 2. Create countries table
    op.create_table(
        'countries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=2), nullable=False),
        sa.Column('code3', sa.String(length=3), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('name_en', sa.String(length=100), nullable=True),
        sa.Column('region', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_countries_id', 'countries', ['id'])
    op.create_index('ix_countries_code', 'countries', ['code'], unique=True)

    # 3. Create backtests table
    op.create_table(
        'backtests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('strategy_id', sa.Integer(), nullable=False),
        sa.Column('instruments', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('timeframe_id', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('initial_capital', sa.Float(), nullable=False),
        sa.Column('final_capital', sa.Float(), nullable=True),
        sa.Column('total_return', sa.Float(), nullable=True),
        sa.Column('annual_return', sa.Float(), nullable=True),
        sa.Column('sharpe_ratio', sa.Float(), nullable=True),
        sa.Column('max_drawdown', sa.Float(), nullable=True),
        sa.Column('total_trades', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('winning_trades', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('losing_trades', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('win_rate', sa.Float(), nullable=True),
        sa.Column('avg_win', sa.Float(), nullable=True),
        sa.Column('avg_loss', sa.Float(), nullable=True),
        sa.Column('profit_factor', sa.Float(), nullable=True),
        sa.Column('metrics', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['strategy_id'], ['strategies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['timeframe_id'], ['timeframes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_backtests_id', 'backtests', ['id'])
    op.create_index('ix_backtests_strategy_id', 'backtests', ['strategy_id'])
    op.create_index('ix_backtests_timeframe_id', 'backtests', ['timeframe_id'])
    op.create_index('ix_backtests_status', 'backtests', ['status'])
    op.create_index('ix_backtests_started_at', 'backtests', ['started_at'])

    # 4. Seed currencies data
    currencies_table = sa.table('currencies',
        sa.column('code', sa.String),
        sa.column('numeric_code', sa.String),
        sa.column('name', sa.String),
        sa.column('name_en', sa.String),
        sa.column('symbol', sa.String),
        sa.column('decimal_places', sa.Integer),
        sa.column('is_active', sa.Integer),
    )

    op.bulk_insert(currencies_table, [
        {'code': 'RUB', 'numeric_code': '643', 'name': 'Российский рубль', 'name_en': 'Russian Ruble', 'symbol': '₽', 'decimal_places': 2, 'is_active': 1},
        {'code': 'USD', 'numeric_code': '840', 'name': 'Доллар США', 'name_en': 'US Dollar', 'symbol': '$', 'decimal_places': 2, 'is_active': 1},
        {'code': 'EUR', 'numeric_code': '978', 'name': 'Евро', 'name_en': 'Euro', 'symbol': '€', 'decimal_places': 2, 'is_active': 1},
        {'code': 'CNY', 'numeric_code': '156', 'name': 'Китайский юань', 'name_en': 'Chinese Yuan', 'symbol': '¥', 'decimal_places': 2, 'is_active': 1},
        {'code': 'GBP', 'numeric_code': '826', 'name': 'Фунт стерлингов', 'name_en': 'Pound Sterling', 'symbol': '£', 'decimal_places': 2, 'is_active': 1},
        {'code': 'JPY', 'numeric_code': '392', 'name': 'Японская иена', 'name_en': 'Japanese Yen', 'symbol': '¥', 'decimal_places': 0, 'is_active': 1},
        {'code': 'BTC', 'numeric_code': None, 'name': 'Bitcoin', 'name_en': 'Bitcoin', 'symbol': '₿', 'decimal_places': 8, 'is_active': 1},
        {'code': 'ETH', 'numeric_code': None, 'name': 'Ethereum', 'name_en': 'Ethereum', 'symbol': 'Ξ', 'decimal_places': 8, 'is_active': 1},
        {'code': 'USDT', 'numeric_code': None, 'name': 'Tether', 'name_en': 'Tether', 'symbol': '₮', 'decimal_places': 6, 'is_active': 1},
    ])

    # 5. Seed countries data
    countries_table = sa.table('countries',
        sa.column('code', sa.String),
        sa.column('code3', sa.String),
        sa.column('name', sa.String),
        sa.column('name_en', sa.String),
        sa.column('region', sa.String),
        sa.column('is_active', sa.Integer),
    )

    op.bulk_insert(countries_table, [
        {'code': 'RU', 'code3': 'RUS', 'name': 'Россия', 'name_en': 'Russia', 'region': 'Europe', 'is_active': 1},
        {'code': 'US', 'code3': 'USA', 'name': 'США', 'name_en': 'United States', 'region': 'Americas', 'is_active': 1},
        {'code': 'GB', 'code3': 'GBR', 'name': 'Великобритания', 'name_en': 'United Kingdom', 'region': 'Europe', 'is_active': 1},
        {'code': 'CN', 'code3': 'CHN', 'name': 'Китай', 'name_en': 'China', 'region': 'Asia', 'is_active': 1},
        {'code': 'JP', 'code3': 'JPN', 'name': 'Япония', 'name_en': 'Japan', 'region': 'Asia', 'is_active': 1},
        {'code': 'DE', 'code3': 'DEU', 'name': 'Германия', 'name_en': 'Germany', 'region': 'Europe', 'is_active': 1},
        {'code': 'FR', 'code3': 'FRA', 'name': 'Франция', 'name_en': 'France', 'region': 'Europe', 'is_active': 1},
    ])

    # 6. Add new columns to instruments table
    op.add_column('instruments', sa.Column('currency_id', sa.Integer(), nullable=True))
    op.add_column('instruments', sa.Column('isin', sa.String(length=12), nullable=True))
    op.add_column('instruments', sa.Column('board', sa.String(length=50), nullable=True))
    op.add_column('instruments', sa.Column('lot_size', sa.Integer(), nullable=True))
    op.add_column('instruments', sa.Column('tick_size', sa.String(length=20), nullable=True))
    op.add_column('instruments', sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True))

    op.create_index('ix_instruments_currency_id', 'instruments', ['currency_id'])
    op.create_foreign_key('fk_instruments_currency', 'instruments', 'currencies', ['currency_id'], ['id'], ondelete='SET NULL')

    # 7. Add new columns to indexes table
    op.add_column('indexes', sa.Column('currency_id', sa.Integer(), nullable=True))
    op.add_column('indexes', sa.Column('country_id', sa.Integer(), nullable=True))

    op.create_index('ix_indexes_currency_id', 'indexes', ['currency_id'])
    op.create_index('ix_indexes_country_id', 'indexes', ['country_id'])
    op.create_foreign_key('fk_indexes_currency', 'indexes', 'currencies', ['currency_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_indexes_country', 'indexes', 'countries', ['country_id'], ['id'], ondelete='SET NULL')


def downgrade():
    # Drop foreign keys and columns from indexes
    op.drop_constraint('fk_indexes_country', 'indexes', type_='foreignkey')
    op.drop_constraint('fk_indexes_currency', 'indexes', type_='foreignkey')
    op.drop_index('ix_indexes_country_id', 'indexes')
    op.drop_index('ix_indexes_currency_id', 'indexes')
    op.drop_column('indexes', 'country_id')
    op.drop_column('indexes', 'currency_id')

    # Drop foreign key and columns from instruments
    op.drop_constraint('fk_instruments_currency', 'instruments', type_='foreignkey')
    op.drop_index('ix_instruments_currency_id', 'instruments')
    op.drop_column('instruments', 'metadata')
    op.drop_column('instruments', 'tick_size')
    op.drop_column('instruments', 'lot_size')
    op.drop_column('instruments', 'board')
    op.drop_column('instruments', 'isin')
    op.drop_column('instruments', 'currency_id')

    # Drop backtests table
    op.drop_index('ix_backtests_started_at', 'backtests')
    op.drop_index('ix_backtests_status', 'backtests')
    op.drop_index('ix_backtests_timeframe_id', 'backtests')
    op.drop_index('ix_backtests_strategy_id', 'backtests')
    op.drop_index('ix_backtests_id', 'backtests')
    op.drop_table('backtests')

    # Drop countries table
    op.drop_index('ix_countries_code', 'countries')
    op.drop_index('ix_countries_id', 'countries')
    op.drop_table('countries')

    # Drop currencies table
    op.drop_index('ix_currencies_code', 'currencies')
    op.drop_index('ix_currencies_id', 'currencies')
    op.drop_table('currencies')
