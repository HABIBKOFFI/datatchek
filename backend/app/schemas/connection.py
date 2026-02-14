import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DBType(str, Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


class ConnectionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    db_type: DBType
    host: str = Field(min_length=1, max_length=255)
    port: int = Field(ge=1, le=65535)
    database: str = Field(min_length=1, max_length=255)
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=255)
    ssl_enabled: bool = False


class ConnectionUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    host: str | None = Field(default=None, max_length=255)
    port: int | None = Field(default=None, ge=1, le=65535)
    database: str | None = Field(default=None, max_length=255)
    username: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, max_length=255)
    ssl_enabled: bool | None = None


class ConnectionResponse(BaseModel):
    id: uuid.UUID
    name: str
    db_type: str
    host: str
    port: int
    database: str
    username: str
    ssl_enabled: bool
    is_active: bool
    last_tested_at: datetime | None
    last_test_status: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConnectionTestResult(BaseModel):
    status: str  # "success" | "failed"
    message: str
