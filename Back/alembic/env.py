from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from dotenv import load_dotenv
import os

from app.database.base import Base
from app.models import (
    User,
    Materiel,
    Request,
    Notification,
    AuditLog,
)

# Charger les variables du fichier .env
load_dotenv()

# Configuration Alembic
config = context.config

# Récupérer DATABASE_URL depuis .env
database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise ValueError(
        "DATABASE_URL n'est pas définie dans le fichier .env"
    )

# Donner l'URL de connexion à Alembic
config.set_main_option("sqlalchemy.url", database_url)

# Configuration du logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Métadonnées de tous nos modèles
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Exécute les migrations en mode offline."""

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Exécute les migrations en mode online."""

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()