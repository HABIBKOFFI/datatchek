from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import TypeDecorator


class PortableJSON(TypeDecorator):
    """JSON type that uses JSONB on PostgreSQL and JSON on other databases.

    This allows models to benefit from PostgreSQL's JSONB indexing in production
    while remaining testable with SQLite in-memory databases.
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())
