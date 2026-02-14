import sqlalchemy as sa
from sqlalchemy.pool import NullPool

from app.config import settings
from app.utils.security import decrypt_value


def create_customer_engine(
    db_type: str,
    host: str,
    port: int,
    database: str,
    username: str,
    encrypted_password: str,
    ssl_enabled: bool = False,
) -> sa.engine.Engine:
    """Create a read-only SQLAlchemy engine for customer database.

    Uses NullPool (no connection pooling) since these are ephemeral
    connections for profiling/analysis, not persistent.
    """
    password = decrypt_value(encrypted_password)

    drivername = {
        "postgresql": "postgresql+psycopg2",
        "mysql": "mysql+pymysql",
    }.get(db_type, "postgresql+psycopg2")

    url = sa.URL.create(
        drivername=drivername,
        username=username,
        password=password,
        host=host,
        port=port,
        database=database,
    )

    connect_args: dict = {
        "connect_timeout": settings.DB_CONNECTION_TIMEOUT_SECONDS,
    }

    # Enforce read-only at connection level for PostgreSQL
    if db_type == "postgresql":
        connect_args["options"] = "-c default_transaction_read_only=on"

    if ssl_enabled:
        connect_args["sslmode"] = "require"

    return sa.create_engine(
        url,
        poolclass=NullPool,
        connect_args=connect_args,
    )


def test_customer_connection(
    db_type: str,
    host: str,
    port: int,
    database: str,
    username: str,
    encrypted_password: str,
    ssl_enabled: bool = False,
) -> dict[str, str]:
    """Test database connection with timeout."""
    try:
        engine = create_customer_engine(
            db_type=db_type,
            host=host,
            port=port,
            database=database,
            username=username,
            encrypted_password=encrypted_password,
            ssl_enabled=ssl_enabled,
        )
        with engine.connect() as conn:
            conn.execute(sa.text("SELECT 1"))

        engine.dispose()
        return {"status": "success", "message": "Connection successful"}
    except Exception as e:
        return {"status": "failed", "message": str(e)}
