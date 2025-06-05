# Chat API Service
POSTMAN Collection Link : https://api.postman.com/collections/6199074-7351beef-3bb6-4ca3-b271-fe1aa9ad1e1f?access_key=PMAT-01JWZNTCTKH0DGRC69PYJ3G6NR     

A FastAPI-based service to manage chat sessions and chat messages.

---

## Getting Started

### Prerequisites

- Docker
- Docker Compose

---

## Setup and Run

1. Clone the repository:

git clone https://github.com/Muraura/rag_chat_storage.git
cd rag_chat_storage

2.Create a .env file
3.Start the application:

docker-compose up --build

API Endpoints
Chat Sessions
GET /chat_sessions/
List all chat sessions (optionally filter by user_id)

POST /chat_sessions/
Create a new chat session

PATCH /chat_sessions/{session_id}
Update a chat session (e.g., name or is_favorite)

DELETE /chat_sessions/{session_id}
Delete a chat session

Chat Messages
GET /chat_messages/?session_id=xxx
List all messages for a specific session

POST /chat_messages/
Add a new message to a session

Swagger UI available at:
http://localhost:8000/docs
