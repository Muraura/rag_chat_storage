# create_tables.py

from src.db_util.models import Base  # Or wherever your models are defined
from src.db_util.connection import CommunicationsSQLAlchemyConnectionManager

def create_all_tables():
    conn = CommunicationsSQLAlchemyConnectionManager()
    engine = conn.engine

    # Create the schema if it doesn't exist (for PostgreSQL)
    with engine.connect() as connection:
        connection.execute(f"CREATE SCHEMA IF NOT EXISTS ragchatstore")

    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    create_all_tables()
