from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from core.db.database import Base
from core.db.models import user, subscription, market_filter, notification_limit
from config.settings import settings


# Alembic config
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for autogenerate
target_metadata = Base.metadata


def get_sync_url() -> str:
    """
    Sync database URL for Alembic
    """
    return settings.database_url_sync


def run_migrations_offline():
    context.configure(
        url=get_sync_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        {"sqlalchemy.url": get_sync_url()},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
