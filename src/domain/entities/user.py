from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4
import re

from src.domain.exceptions import InvalidEmailException, InvalidUsernameException


@dataclass
class User:
    id: UUID
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, email: str, username: str, full_name: Optional[str] = None) -> "User":
        cls._validate_email(email)
        cls._validate_username(username)
        
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            email=email.lower().strip(),
            username=username.strip(),
            full_name=full_name.strip() if full_name else None,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _validate_email(email: str) -> None:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise InvalidEmailException(f"Invalid email format: {email}")

    @staticmethod
    def _validate_username(username: str) -> None:
        if len(username) < 3:
            raise InvalidUsernameException("Username must be at least 3 characters long")
        if len(username) > 100:
            raise InvalidUsernameException("Username must be at most 100 characters long")
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise InvalidUsernameException("Username can only contain letters, numbers, and underscores")

    def update(self, email: Optional[str] = None, username: Optional[str] = None, full_name: Optional[str] = None) -> None:
        if email is not None:
            self._validate_email(email)
            self.email = email.lower().strip()
        if username is not None:
            self._validate_username(username)
            self.username = username.strip()
        if full_name is not None:
            self.full_name = full_name.strip() if full_name.strip() else None
        self.updated_at = datetime.now(timezone.utc)

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)

    def activate(self) -> None:
        self.is_active = True
        self.updated_at = datetime.now(timezone.utc)

