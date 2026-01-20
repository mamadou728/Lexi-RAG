from beanie import Document, Indexed
from pydantic import Field, EmailStr
from enum import Enum
from datetime import datetime, timezone

class SystemRole(str, Enum):
    PARTNER = "partner"
    ASSOCIATE = "associate"
    STAFF = "staff"
    CLIENT = "client"

class AccountStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"

class User(Document):
    # Indexed(..., unique=True) ensures no two users have the same email
    email: Indexed(EmailStr, unique=True) 
    password_hash: str
    full_name: str
    
    # Strict Enums
    system_role: SystemRole = SystemRole.ASSOCIATE
    account_status: AccountStatus = AccountStatus.PENDING
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "users"