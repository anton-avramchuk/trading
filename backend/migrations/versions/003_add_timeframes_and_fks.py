"""Add timeframes table and foreign keys

Revision ID: 003
Revises: 002
Create Date: 2024-12-03 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '003'
down_revision = 'c5c3be7757d8'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Создание таблицы timeframes
    op.create_table(
        'timeframes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('minutes', sa.Integer(), nullable=False),
        sa.Column('moex_interval', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_timeframes_id'), 'timeframes', ['id'], unique=False)
    op.create_index(op.f('ix_timeframes_code'), 'timeframes', ['code'], unique=True)
    op.create_index(op.f('ix_timeframes_minutes'), 'timeframes', ['minutes'], unique=False)

    # 2. Заполнение таблицы timeframes начальными данными
    timeframes_table = sa.table(
        'timeframes',
        sa.column('code', sa.String),
        sa.column('name', sa.String),
        sa.column('description', sa.Text),
        sa.column('minutes', sa.Integer),
        sa.column('moex_interval', sa.Integer),
        sa.column('created_at', sa.DateTime),
        sa.column('is_active', sa.Integer),
    )

    op.bulk_insert(
        timeframes_table,
        [
            {
                'code': '1m',
                'name': '1 минута',
                'description': 'Минутный таймфрейм',
                'minutes': 1,
                'moex_interval': 1,
                'created_at': datetime.utcnow(),
                'is_active': 1
            },
            {
                'code': '10m',
                'name': '10 минут',
                'description': '10-минутный таймфрейм',
                'minutes': 10,
                'moex_interval': 10,
                'created_at': datetime.utcnow(),
                'is_active': 1
            },
            {
                'code': '1h',
                'name': '1 час',
                'description': 'Часовой таймфрейм',
                'minutes': 60,
                'moex_interval': 60,
                'created_at': datetime.utcnow(),
                'is_active': 1
            },
            {
                'code': '1d',
                'name': '1 день',
                'description': 'Дневной таймфрейм',
                'minutes': 1440,
                'moex_interval': 24,
                'created_at': datetime.utcnow(),
                'is_active': 1
            },
            {
                'code': '1w',
                'name': '1 неделя',
                'description': 'Недельный таймфрейм',
                'minutes': 10080,
                'moex_interval': 7,
                'created_at': datetime.utcnow(),
                'is_active': 1
            },
            {
                'code': '1M',
                'name': '1 месяц',
                'description': 'Месячный таймфрейм',
                'minutes': 43200,
                'moex_interval': 31,
                'created_at': datetime.utcnow(),
                'is_active': 1
            },
            {
                'code': '1Q',
                'name': '1 квартал',
                'description': 'Квартальный таймфрейм',
                'minutes': 129600,
                'moex_interval': 4,
                'created_at': datetime.utcnow(),
                'is_active': 1
            },
        ]
    )

    # 3. Добавление колонки timeframe_id в ohlcv
    op.add_column('ohlcv', sa.Column('timeframe_id', sa.Integer(), nullable=True))

    # 4. Заполнение timeframe_id на основе существующих данных
    # Получаем connection для выполнения SQL
    conn = op.get_bind()

    # Обновляем timeframe_id для каждого кода
    timeframe_mapping = [
        ('1m', 1),
        ('10m', 2),
        ('1h', 3),
        ('1d', 4),
        ('1w', 5),
        ('1M', 6),
        ('1Q', 7),
    ]

    for code, tf_id in timeframe_mapping:
        conn.execute(
            sa.text(f"UPDATE ohlcv SET timeframe_id = {tf_id} WHERE timeframe = '{code}'")
        )

    # 5. Делаем timeframe_id NOT NULL и добавляем FK
    op.alter_column('ohlcv', 'timeframe_id', nullable=False)
    op.create_foreign_key(
        'fk_ohlcv_timeframe',
        'ohlcv',
        'timeframes',
        ['timeframe_id'],
        ['id']
    )
    op.create_index(op.f('ix_ohlcv_timeframe_id'), 'ohlcv', ['timeframe_id'], unique=False)

    # 6. Обновление UNIQUE constraint в ohlcv
    op.drop_constraint('uq_instrument_timeframe_timestamp', 'ohlcv', type_='unique')
    op.create_unique_constraint(
        'uq_instrument_timeframe_timestamp',
        'ohlcv',
        ['instrument_id', 'timeframe_id', 'timestamp']
    )

    # 7. Обновление composite index в ohlcv
    op.drop_index('idx_instrument_timeframe_time', table_name='ohlcv')
    op.create_index(
        'idx_instrument_timeframe_time',
        'ohlcv',
        ['instrument_id', 'timeframe_id', 'timestamp']
    )

    # 8. Добавление колонки strategy_id в signals
    op.add_column('signals', sa.Column('strategy_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_signals_strategy',
        'signals',
        'strategies',
        ['strategy_id'],
        ['id'],
        ondelete='SET NULL'
    )
    op.create_index(op.f('ix_signals_strategy_id'), 'signals', ['strategy_id'], unique=False)

    # 9. Обновление FK instruments.index_id с ondelete
    op.drop_constraint('instruments_index_id_fkey', 'instruments', type_='foreignkey')
    op.create_foreign_key(
        'fk_instruments_index',
        'instruments',
        'indexes',
        ['index_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # 10. Обновление FK ohlcv.instrument_id с ondelete CASCADE
    op.drop_constraint('ohlcv_instrument_id_fkey', 'ohlcv', type_='foreignkey')
    op.create_foreign_key(
        'fk_ohlcv_instrument',
        'ohlcv',
        'instruments',
        ['instrument_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # 11. Обновление FK signals.instrument_id с ondelete CASCADE
    op.drop_constraint('signals_instrument_id_fkey', 'signals', type_='foreignkey')
    op.create_foreign_key(
        'fk_signals_instrument',
        'signals',
        'instruments',
        ['instrument_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade():
    # Откат изменений в обратном порядке

    # 11. Восстановление FK signals.instrument_id
    op.drop_constraint('fk_signals_instrument', 'signals', type_='foreignkey')
    op.create_foreign_key(
        'signals_instrument_id_fkey',
        'signals',
        'instruments',
        ['instrument_id'],
        ['id']
    )

    # 10. Восстановление FK ohlcv.instrument_id
    op.drop_constraint('fk_ohlcv_instrument', 'ohlcv', type_='foreignkey')
    op.create_foreign_key(
        'ohlcv_instrument_id_fkey',
        'ohlcv',
        'instruments',
        ['instrument_id'],
        ['id']
    )

    # 9. Восстановление FK instruments.index_id
    op.drop_constraint('fk_instruments_index', 'instruments', type_='foreignkey')
    op.create_foreign_key(
        'instruments_index_id_fkey',
        'instruments',
        'indexes',
        ['index_id'],
        ['id']
    )

    # 8. Удаление strategy_id из signals
    op.drop_index(op.f('ix_signals_strategy_id'), table_name='signals')
    op.drop_constraint('fk_signals_strategy', 'signals', type_='foreignkey')
    op.drop_column('signals', 'strategy_id')

    # 7. Восстановление старого composite index в ohlcv
    op.drop_index('idx_instrument_timeframe_time', table_name='ohlcv')
    op.create_index(
        'idx_instrument_timeframe_time',
        'ohlcv',
        ['instrument_id', 'timeframe', 'timestamp']
    )

    # 6. Восстановление старого UNIQUE constraint в ohlcv
    op.drop_constraint('uq_instrument_timeframe_timestamp', 'ohlcv', type_='unique')
    op.create_unique_constraint(
        'uq_instrument_timeframe_timestamp',
        'ohlcv',
        ['instrument_id', 'timeframe', 'timestamp']
    )

    # 5. Удаление FK и колонки timeframe_id
    op.drop_index(op.f('ix_ohlcv_timeframe_id'), table_name='ohlcv')
    op.drop_constraint('fk_ohlcv_timeframe', 'ohlcv', type_='foreignkey')
    op.drop_column('ohlcv', 'timeframe_id')

    # 1. Удаление таблицы timeframes
    op.drop_index(op.f('ix_timeframes_minutes'), table_name='timeframes')
    op.drop_index(op.f('ix_timeframes_code'), table_name='timeframes')
    op.drop_index(op.f('ix_timeframes_id'), table_name='timeframes')
    op.drop_table('timeframes')
