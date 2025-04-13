from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.models.database import Base
import enum


class CredentialType(enum.Enum):
    API_KEY = "api_key"
    ACCESS_TOKEN = "access_token"
    SECRET_KEY = "secret_key"
    PASSWORD = "password"
    OTHER = "other"
    COOKIES = "cookies"


class Credential(Base):
    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True, index=True)
    owner = Column(String, index=True, nullable=False)
    credential = Column(String, nullable=False)
    credential_type = Column(Enum(CredentialType),
                             nullable=False, default=CredentialType.OTHER)
    expire_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC),
                        onupdate=lambda: datetime.now(UTC))

    def __repr__(self):
        return f"<Credential(id={self.id}, owner={self.owner}, type={self.credential_type}, expire_time={self.expire_time})>"
