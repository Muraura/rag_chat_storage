from sqlalchemy import Column, Integer, String, JSON, DATETIME, TEXT, Index
from sqlalchemy.ext.declarative import declarative_base
from src.db_util.connection import CommunicationsSQLAlchemyConnectionManager

sql_obj = CommunicationsSQLAlchemyConnectionManager()
Base = declarative_base()
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


class SenderEnum(str, enum.Enum):
    user = "user"
    assistant = "assistant"
    __table_args__ = {"schema": "ragchatstore"}


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=True)

    sessions = relationship("ChatSession", back_populates="user")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    name = Column(String, nullable=True)
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatSession id={self.id} name={self.name} user_id={self.user_id} favorite={self.is_favorite}>"


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("ragchatstore.chat_sessions.id", ondelete="CASCADE"))
    sender = Column(Enum(SenderEnum), nullable=False)
    content = Column(Text, nullable=False)
    context = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    session = relationship("ChatSession", back_populates="messages")





# class Company(Base):
#     __tablename__ = 'integration_companies'
#     __table_args__ = {"schema": "talent500_share"}
#     id = Column(Integer, primary_key=True)
#     company_name = Column(String(200), nullable=False)
#     company_group = Column(String(200), nullable=False)
#     ATS = Column(String(200), nullable=False)
#
#     def __repr__(self):
#         return f" id : {self.id}, company_name : {self.company_name} ,company_group : {self.company_group},ATS : {self.ATS}"

#
# class Transaction(Base):
#     __tablename__ = 'integration_transactions'
#     __table_args__ = {"schema": "talent500_share"}
#     id = Column(String(200), primary_key=True)
#     s3_file_name = Column(String(200), nullable=False)
#     entity = Column(String(200), nullable=False)
#     entity_unique_id = Column(String(200), nullable=False)
#     source = Column(String(200), nullable=False)
#     destination = Column(String(200), nullable=False)
#     company = Column(Integer, nullable=False)
#     status = Column(String(200))
#
#     def __repr__(self):
#         return f" id : {self.id}, entity : {self.entity} "
#
#
# class Mapping(Base):
#     __tablename__ = 'integration_mappings'
#     __table_args__ = {"schema": "talent500_share"}
#     id = Column(Integer, primary_key=True)
#     source = Column(String(200), nullable=False)
#     destination = Column(String(200), nullable=False)
#     entity = Column(String(200), nullable=False)
#     mapping = Column(JSON, nullable=False)
#
#     def __repr__(self):
#         return f" id : {self.id}, source : {self.source},destination : {self.destination}, entity : {self.entity},mapping : {self.mapping}"
#
#
# class KafkaMapping(Base):
#     __tablename__ = 'integration_kafka_mappings'
#     __table_args__ = {"schema": "talent500_share"}
#     id = Column(Integer, primary_key=True)
#     client_group = Column(String(200), nullable=False)
#     entity = Column(String(200), nullable=False)
#     topic = Column(String(200), nullable=False)
#     partitions = Column(String(200), nullable=False)
#     retry_topic = Column(String(200), nullable=False)
#     no_of_retries = Column(String(200), nullable=False)
#     dl_topic = Column(String(200), nullable=False)
#     consumer_group = Column(String(200))
#     kafka_broker = Column(String(200))
#     compression_type = Column(String(100))
#     batch_size = Column(String(100))
#
#     def __repr__(self):
#         return f" id : {self.id}, topic : {self.topic},kafka_broker : {self.kafka_broker},consumer_group : {self.consumer_group}"
#
#
# class RunHistory(Base):
#     __tablename__ = 'integration_run_history'
#     __table_args__ = {"schema": "talent500_share"}
#
#     id = Column(Integer, primary_key=True)
#     company_id = Column(Integer, nullable=False)
#     entity = Column(String(200), nullable=False)
#     last_run_utc = Column(DATETIME, nullable=False, default=datetime.datetime.utcnow())
#     from_date = Column(DATETIME, nullable=False)
#     to_date = Column(DATETIME, nullable=False)
#
#     def __repr__(self):
#         return f" id : {self.id}, entity : {self.entity}, company_id : {self.company_id}, last_run_utc : {self.last_run_utc}, from_date : {self.from_date}, to_date : {self.to_date}"
#
#
# class SFTPIntegrationJob(Base):
#     __tablename__ = 'integration_sftp_jobs'
#     __table_args__ = {"schema": "talent500_share"}
#
#     id = Column(String(200), primary_key=True)
#     company_id = Column(Integer, nullable=False)
#     entity = Column(String(200), nullable=False)
#     query = Column(TEXT, nullable=False)
#     status = Column(String(50), nullable=False)
#     message = Column(TEXT)
#     remote_filename = Column(String(500))
#     rows_processed = Column(Integer)
#     client_name = Column(String(100))
#     created_at = Column(DATETIME, nullable=False, default=datetime.datetime.now())
#     updated_at = Column(DATETIME, nullable=False, default=datetime.datetime.now())
#
#     def __repr__(self):
#         return f" id : {self.id}, entity : {self.entity}, company_id : {self.company_id}, status : {self.status}, client_name : {self.client_name}, created_at : {self.created_at}"
#
#
# Base.metadata.create_all(sql_obj.engine)
