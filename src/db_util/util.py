from sqlalchemy.orm import Session
from .connection import CommunicationsSQLAlchemyConnectionManager

connection = CommunicationsSQLAlchemyConnectionManager()


def get_db() -> Session:
    if connection.Session is None:
        connection.refresh_session()
    db = connection.Session()
    try:
        yield db
    finally:
        db.close()
