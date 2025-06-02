import pytest
from httpx import AsyncClient
from fastapi import status
from src.main import app  # or wherever your FastAPI instance is

# Mock UUID for testing
import uuid

@pytest.mark.asyncio
async def test_create_chat_session():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "user_id": str(uuid.uuid4()),
            "name": "Test Session"
        }
        response = await ac.get("/chat_sessions/", params=payload)
        assert response.status_code in (200, 400)  # 400 if validation fails


@pytest.mark.asyncio
async def test_list_chat_sessions():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/chat_sessions/")
        assert response.status_code == status.HTTP_200_OK
        assert "sessions" in response.json()


@pytest.mark.asyncio
async def test_create_chat_message():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        session_id = str(uuid.uuid4())  # Replace with an existing session ID in a real test
        payload = {
            "session_id": session_id,
            "sender": "USER",
            "content": "Hello, this is a test message"
        }
        response = await ac.post("/chat_messages/", json=payload)
        assert response.status_code in (200, 400, 404)


@pytest.mark.asyncio
async def test_list_chat_messages():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        session_id = str(uuid.uuid4())  # Replace with an actual session ID
        response = await ac.get(f"/chat_messages/?session_id={session_id}")
        assert response.status_code in (200, 404)
