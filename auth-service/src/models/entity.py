import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from .base import Base, TimestampMixin


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    username = Column(String(50))
    has_2fa = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=True)
    role = relationship("Role", uselist=False, lazy="selectin")
    refresh_token = relationship(
        "RefreshToken",
        uselist=False,
        back_populates="user",
        cascade="delete, delete-orphan",
    )
    devices = relationship("Device", back_populates="user", cascade="all, delete-orphan")
    social_accounts = relationship("SocialAccount", back_populates="user", cascade="all, delete-orphan")

    def __init__(self, email: str, password: str, username: str, **kw: Any) -> None:
        super().__init__(**kw)
        self.email = email
        self.password = generate_password_hash(password)
        self.username = username

    def is_password_valid(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class SocialAccount(Base, TimestampMixin):
    __tablename__ = "social_account"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship(User, uselist=False, lazy="selectin")

    social_id = Column(String, nullable=False)
    social_name = Column(String, nullable=False)

    __table_args__ = (UniqueConstraint("social_id", "social_name", name="social_pk"),)

    def __repr__(self):
        return f"<SocialAccount {self.social_name}:{self.user_id}>"


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    token = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="refresh_token", lazy="selectin")

    def __init__(self, token: str, user_id: uuid, **kw: Any):
        super().__init__(**kw)
        self.token = token
        self.user_id = user_id


class Device(Base):
    __tablename__ = "devices"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_agent = Column(String, nullable=False)
    screen_width = Column(Integer, nullable=True)
    screen_height = Column(Integer, nullable=True)
    timezone = Column(String, nullable=True)
    last_login = Column(DateTime, default=datetime.utcnow)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="devices")

    def __init__(
        self,
        user_agent: str,
        screen_width: int,
        screen_height: int,
        timezone: str,
        user_id: uuid,
        **kw: Any,
    ):
        super().__init__(**kw)
        self.user_agent = user_agent
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.timezone = timezone
        self.user_id = user_id

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "user_agent",
            "screen_width",
            "screen_height",
            "timezone",
            name="uq_device_details",
        ),
    )
