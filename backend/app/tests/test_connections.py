import uuid
from unittest.mock import patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestConnectionsCRUD:
    @patch("app.api.connections.test_customer_connection")
    async def test_create_connection(
        self, mock_test, client: AsyncClient, auth_headers
    ):
        mock_test.return_value = {"status": "success", "message": "OK"}

        response = await client.post(
            "/api/v1/connections",
            json={
                "name": "Test DB",
                "db_type": "postgresql",
                "host": "localhost",
                "port": 5432,
                "database": "test_db",
                "username": "user",
                "password": "pass",
                "ssl_enabled": False,
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test DB"
        assert data["db_type"] == "postgresql"
        assert data["last_test_status"] == "success"
        # Password must never be in response
        assert "encrypted_password" not in data
        assert "password" not in data

    @patch("app.api.connections.test_customer_connection")
    async def test_create_connection_test_fails(
        self, mock_test, client: AsyncClient, auth_headers
    ):
        mock_test.return_value = {"status": "failed", "message": "Connection refused"}

        response = await client.post(
            "/api/v1/connections",
            json={
                "name": "Bad DB",
                "db_type": "postgresql",
                "host": "badhost",
                "port": 5432,
                "database": "nodb",
                "username": "user",
                "password": "pass",
            },
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "Connection test failed" in response.json()["detail"]

    async def test_create_connection_no_auth(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/connections",
            json={
                "name": "Test",
                "db_type": "postgresql",
                "host": "localhost",
                "port": 5432,
                "database": "db",
                "username": "user",
                "password": "pass",
            },
        )
        assert response.status_code == 401

    @patch("app.api.connections.test_customer_connection")
    async def test_list_connections(
        self, mock_test, client: AsyncClient, auth_headers
    ):
        mock_test.return_value = {"status": "success", "message": "OK"}

        # Create two connections
        for i in range(2):
            await client.post(
                "/api/v1/connections",
                json={
                    "name": f"DB {i}",
                    "db_type": "postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "database": f"db_{i}",
                    "username": "user",
                    "password": "pass",
                },
                headers=auth_headers,
            )

        response = await client.get("/api/v1/connections", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @patch("app.api.connections.test_customer_connection")
    async def test_get_connection(
        self, mock_test, client: AsyncClient, auth_headers
    ):
        mock_test.return_value = {"status": "success", "message": "OK"}

        create_resp = await client.post(
            "/api/v1/connections",
            json={
                "name": "My DB",
                "db_type": "mysql",
                "host": "localhost",
                "port": 3306,
                "database": "mydb",
                "username": "user",
                "password": "pass",
            },
            headers=auth_headers,
        )
        conn_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/v1/connections/{conn_id}", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["name"] == "My DB"

    async def test_get_nonexistent_connection(
        self, client: AsyncClient, auth_headers
    ):
        fake_id = uuid.uuid4()
        response = await client.get(
            f"/api/v1/connections/{fake_id}", headers=auth_headers
        )
        assert response.status_code == 404

    @patch("app.api.connections.test_customer_connection")
    async def test_delete_connection(
        self, mock_test, client: AsyncClient, auth_headers
    ):
        mock_test.return_value = {"status": "success", "message": "OK"}

        create_resp = await client.post(
            "/api/v1/connections",
            json={
                "name": "To Delete",
                "db_type": "postgresql",
                "host": "localhost",
                "port": 5432,
                "database": "todelete",
                "username": "user",
                "password": "pass",
            },
            headers=auth_headers,
        )
        conn_id = create_resp.json()["id"]

        response = await client.delete(
            f"/api/v1/connections/{conn_id}", headers=auth_headers
        )
        assert response.status_code == 204

        # Verify it's gone
        response = await client.get(
            f"/api/v1/connections/{conn_id}", headers=auth_headers
        )
        assert response.status_code == 404

    async def test_invalid_db_type(self, client: AsyncClient, auth_headers):
        response = await client.post(
            "/api/v1/connections",
            json={
                "name": "Bad Type",
                "db_type": "mongodb",
                "host": "localhost",
                "port": 27017,
                "database": "test",
                "username": "user",
                "password": "pass",
            },
            headers=auth_headers,
        )
        assert response.status_code == 422

    async def test_invalid_port(self, client: AsyncClient, auth_headers):
        response = await client.post(
            "/api/v1/connections",
            json={
                "name": "Bad Port",
                "db_type": "postgresql",
                "host": "localhost",
                "port": 99999,
                "database": "test",
                "username": "user",
                "password": "pass",
            },
            headers=auth_headers,
        )
        assert response.status_code == 422
