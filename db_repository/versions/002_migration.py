from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
posts = Table('posts', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('userid', Integer),
    Column('start_date', String(length=50)),
    Column('end_date', String(length=50)),
    Column('status', Boolean),
    Column('deal_date', String(length=50)),
    Column('post_value', Float(precision=20)),
    Column('post_direction', Boolean),
    Column('post_type_id', Integer),
    Column('remark', String(length=500)),
)

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
    Column('status', Boolean, default=ColumnDefault(True)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['posts'].columns['remark'].create()
    post_meta.tables['user'].columns['status'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['posts'].columns['remark'].drop()
    post_meta.tables['user'].columns['status'].drop()
