from __future__ import annotations
from .base_model import *


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[UUIDpk]
    tg_user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    status: Mapped[ApplicationStatus] = mapped_column(default=ApplicationStatus.pending)
    invite_id: Mapped[str] = mapped_column(UUID(as_uuid=True), default=uuid4)
    invite: Mapped["Invite | None"] = relationship(back_populates="application")

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at] 

    