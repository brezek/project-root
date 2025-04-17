import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ✅ Import the Base from your models to enable autogenerate feature
from models import Base  # Ensure correct path

# ✅ Load Alembic config
config = context.config

# ✅ Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ✅ Set up the metadata for Alembic to use
target_metadata = Base.metadata  # This enables autogenerate

# ✅ Database URL - Use either alembic.ini OR environment variable
db_url = config.get_main_option("sqlalchemy.url") or os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("❌ DATABASE_URL is not set in alembic.ini or environment variables.")

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (without connecting to DB)."""
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode (with a live DB connection)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
