import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.connection_manager import test_customer_connection
from app.database import get_db
from app.models.connection import Connection
from app.models.user import User
from app.schemas.connection import (
    ConnectionCreate,
    ConnectionResponse,
    ConnectionTestResult,
    ConnectionUpdate,
)
from app.utils.security import encrypt_value

router = APIRouter()


@router.post(
    "",
    response_model=ConnectionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_connection(
    data: ConnectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Connection:
    # Encrypt password before storage
    encrypted_pw = encrypt_value(data.password)

    # Test connection before saving
    test_result = test_customer_connection(
        db_type=data.db_type.value,
        host=data.host,
        port=data.port,
        database=data.database,
        username=data.username,
        encrypted_password=encrypted_pw,
        ssl_enabled=data.ssl_enabled,
    )

    if test_result["status"] == "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Connection test failed: {test_result['message']}",
        )

    connection = Connection(
        user_id=current_user.id,
        name=data.name,
        db_type=data.db_type.value,
        host=data.host,
        port=data.port,
        database=data.database,
        username=data.username,
        encrypted_password=encrypted_pw,
        ssl_enabled=data.ssl_enabled,
        last_tested_at=datetime.utcnow(),
        last_test_status="success",
    )
    db.add(connection)
    await db.flush()
    await db.refresh(connection)
    return connection


@router.get("", response_model=list[ConnectionResponse])
async def list_connections(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Connection]:
    result = await db.execute(
        select(Connection)
        .where(Connection.user_id == current_user.id)
        .order_by(Connection.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{connection_id}", response_model=ConnectionResponse)
async def get_connection(
    connection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Connection:
    connection = await _get_user_connection(db, connection_id, current_user.id)
    return connection


@router.put("/{connection_id}", response_model=ConnectionResponse)
async def update_connection(
    connection_id: uuid.UUID,
    data: ConnectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Connection:
    connection = await _get_user_connection(db, connection_id, current_user.id)

    update_data = data.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["encrypted_password"] = encrypt_value(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(connection, field, value)

    connection.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(connection)
    return connection


@router.delete("/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connection(
    connection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    connection = await _get_user_connection(db, connection_id, current_user.id)
    await db.delete(connection)


@router.post("/{connection_id}/test", response_model=ConnectionTestResult)
async def test_connection(
    connection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    connection = await _get_user_connection(db, connection_id, current_user.id)

    result = test_customer_connection(
        db_type=connection.db_type,
        host=connection.host,
        port=connection.port,
        database=connection.database,
        username=connection.username,
        encrypted_password=connection.encrypted_password,
        ssl_enabled=connection.ssl_enabled,
    )

    connection.last_tested_at = datetime.utcnow()
    connection.last_test_status = result["status"]
    await db.flush()

    return result


async def _get_user_connection(
    db: AsyncSession,
    connection_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Connection:
    """Fetch a connection ensuring it belongs to the current user."""
    result = await db.execute(
        select(Connection).where(
            Connection.id == connection_id,
            Connection.user_id == user_id,
        )
    )
    connection = result.scalar_one_or_none()
    if connection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )
    return connection
