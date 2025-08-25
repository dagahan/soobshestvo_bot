from __future__ import annotations
from .base_model import *


class Member(Base):
    __tablename__ = "members"
    
    id: Mapped[UUIDpk]
    user_name: Mapped[str] = mapped_column(String(32), nullable=False) 
    first_name: Mapped[str] = mapped_column(String(32), nullable=False)
    last_name: Mapped[str] = mapped_column(String(32), nullable=False)
    role: Mapped[MemberRole] = mapped_column(
        SQLEnum(MemberRole.member, MemberRole.admin, MemberRole.god, name="role"),
        default=MemberRole.member,
        nullable=False,
    )
    bio: Mapped[str] = mapped_column(Text, default="", server_default="")

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


