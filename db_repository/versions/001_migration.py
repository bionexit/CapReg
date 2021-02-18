from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('username', String(length=32)),
    Column('role_id', Integer),
    Column('password_hash', String(length=128)),
    Column('contact_name', String(length=64)),
    Column('phone', String(length=12)),
    Column('value_usble', Float(precision=20)),
    Column('trade_num', String(length=12)),
    Column('reg_date', String(length=50), default=ColumnDefault('CURRENT_TIMESTAMP')),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].columns['value_usble'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].columns['value_usble'].drop()
