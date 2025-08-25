from __future__ import annotations
from .base_model import *


class Invite(Base):
    __tablename__ = "invites"

    id: Mapped[UUIDpk]
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    invite_link: Mapped[str] = mapped_column(String(256), unique=True)
    intended_user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    expire_at: Mapped[UnixTs]
    member_limit: Mapped[int] = mapped_column(Integer, default=1)
    creates_join_request: Mapped[bool] = mapped_column(Boolean, default=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)

    application: Mapped["Application | None"] = relationship(
        back_populates="invite", uselist=False
    ) 

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


