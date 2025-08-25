from typing import Annotated
from uuid import UUID, uuid4
import bcrypt
from loguru import logger

from sqlalchemy import (
    TIMESTAMP, # Unix time, seconds since 1970-01-01T00:00:00Z, may be negative before 1970
    BigInteger,
    Boolean,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
    TypeDecorator,
    text,
    Table,
    Column,
    UniqueConstraint,
    Text,
)

from enum import Enum as PyEnum

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


UUIDpk = Annotated[UUID,
        mapped_column(UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )]

UnixTs = Annotated[int, mapped_column(BigInteger, nullable=False)]

created_at = Annotated[int, mapped_column(
    BigInteger,
    server_default=text("(EXTRACT(EPOCH FROM NOW()))::bigint"),
    nullable=False)
]

updated_at = Annotated[int, mapped_column(
    BigInteger,
    server_default=text("(EXTRACT(EPOCH FROM NOW()))::bigint"),
    onupdate=text("(EXTRACT(EPOCH FROM NOW()))::bigint"),
    nullable=False)
]

money = Annotated[Numeric, mapped_column(Numeric(10, 2), nullable=False)]


class Base(DeclarativeBase):
    # this is base class for all of declaratively using models of tables.
    # e.g. we use this for create or drop all of tables in db.
    pass


class MemberRole(str, PyEnum):
    member = "member"
    admin = "admin"
    god = "god"


class ApplicationStatus(str, PyEnum):
    pending = "pending"
    approved = "approved"
    
    

