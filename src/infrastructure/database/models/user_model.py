from uuid import uuid4

from sqlalchemy import Column, String, Boolean, DateTime, func, Index
from sqlalchemy.dialects.mysql import CHAR

from src.infrastructure.database.base import Base


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("idx_email", "email"),
        Index("idx_username", "username"),
        Index("idx_created_at", "created_at"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid4()), index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<UserModel(id={self.id}, email={self.email})>"

