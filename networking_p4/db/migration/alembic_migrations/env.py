from alembic import context
from neutron_lib.db import model_base
from oslo_config import cfg
import sqlalchemy as sa
from sqlalchemy import event

from neutron.db.migration.alembic_migrations import external
from neutron.db.migration import autogen
from neutron.db.migration.connection import DBConnection

MYSQL_ENGINE = None
P4_VERSION_TABLE = 'alembic_version_p4'
config = context.config
neutron_config = config.neutron_config
target_metadata = model_base.BASEV2.metadata

def set_mysql_engine():
    try:
        mysql_engine = neutron_config.command.mysql_engine
    except cfg.NoSuchOptError:
        mysql_engine = None

    global MYSQL_ENGINE
    MYSQL_ENGINE = (mysql_engine or
                    model_base.BASEV2.__table_args__['mysql_engine'])


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with either a URL
    or an Engine.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    set_mysql_engine()

    kwargs = dict()
    if neutron_config.database.connection:
        kwargs['url'] = neutron_config.database.connection
    else:
        kwargs['dialect_name'] = neutron_config.database.engine
    kwargs['version_table'] = P4_VERSION_TABLE
    context.configure(**kwargs)

    with context.begin_transaction():
        context.run_migrations()


@event.listens_for(sa.Table, 'after_parent_attach')
def set_storage_engine(target, parent):
    if MYSQL_ENGINE:
        target.kwargs['mysql_engine'] = MYSQL_ENGINE


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    set_mysql_engine()
    connection = config.attributes.get('connection')
    with DBConnection(neutron_config.database.connection, connection) as conn:
        context.configure(
            connection=conn,
            target_metadata=target_metadata,
            version_table=P4_VERSION_TABLE,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()