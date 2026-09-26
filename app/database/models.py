"""
Multi-Tenant Application Database Models.
Defines Organization, User, DatabaseConnection, and QueryHistory entities.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    connections = relationship("DatabaseConnection", back_populates="organization", cascade="all, delete-orphan")
    query_history = relationship("QueryHistoryItem", back_populates="organization", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="member", nullable=False)  # 'owner', 'admin', 'member'
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    queries = relationship("QueryHistoryItem", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class DatabaseConnection(Base):
    __tablename__ = "database_connections"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    db_type = Column(String(20), nullable=False)  # 'postgresql', 'mysql', 'sqlite'
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    database_name = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False)
    encrypted_password = Column(Text, nullable=False)
    ssl_enabled = Column(Boolean, default=False, nullable=False)
    schema_cache = Column(Text, nullable=True)  # JSON string of introspected schema
    last_synced_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="connections")
    queries = relationship("QueryHistoryItem", back_populates="connection", cascade="all, delete-orphan")

    def to_safe_dict(self):
        """Returns connection representation with credentials strictly masked."""
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "name": self.name,
            "db_type": self.db_type,
            "host": self.host,
            "port": self.port,
            "database_name": self.database_name,
            "username": self.username,
            "ssl_enabled": self.ssl_enabled,
            "has_schema": bool(self.schema_cache),
            "last_synced_at": self.last_synced_at.isoformat() if self.last_synced_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class QueryHistoryItem(Base):
    __tablename__ = "query_history"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    connection_id = Column(String(36), ForeignKey("database_connections.id", ondelete="SET NULL"), nullable=True, index=True)
    
    natural_language_query = Column(Text, nullable=False)
    clarification_question = Column(Text, nullable=True)
    clarification_answer = Column(Text, nullable=True)
    resolved_intent = Column(Text, nullable=True)
    generated_sql = Column(Text, nullable=True)
    execution_status = Column(String(30), nullable=False)  # 'success', 'error', 'clarification_required'
    row_count = Column(Integer, default=0, nullable=False)
    execution_time_ms = Column(Float, default=0.0, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False, index=True)

    # Relationships
    organization = relationship("Organization", back_populates="query_history")
    user = relationship("User", back_populates="queries")
    connection = relationship("DatabaseConnection", back_populates="queries")

    def to_dict(self):
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "user_id": self.user_id,
            "connection_id": self.connection_id,
            "natural_language_query": self.natural_language_query,
            "clarification_question": self.clarification_question,
            "clarification_answer": self.clarification_answer,
            "resolved_intent": self.resolved_intent,
            "generated_sql": self.generated_sql,
            "execution_status": self.execution_status,
            "row_count": self.row_count,
            "execution_time_ms": self.execution_time_ms,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
