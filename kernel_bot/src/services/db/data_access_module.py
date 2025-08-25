# pyright: strict
from __future__ import annotations
from typing import Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    Member,
    MemberRole,
    Application,
    ApplicationStatus,
    Invite,
)


class MemberDAO:
    @staticmethod
    async def get_by_id(session: AsyncSession, member_id: UUID) -> Optional[Member]:
        res = await session.execute(select(Member).where(Member.id == member_id))
        return res.scalar_one_or_none()


    @staticmethod
    async def get_by_username(session: AsyncSession, username: str) -> Optional[Member]:
        res = await session.execute(select(Member).where(Member.user_name == username))
        return res.scalar_one_or_none()


    @staticmethod
    async def create(
        session: AsyncSession,
        *,
        user_name: str,
        first_name: str,
        last_name: str,
        role: MemberRole = MemberRole.member,
        bio: str = "",
    ) -> Member:
        obj = Member(
            user_name=user_name,
            first_name=first_name,
            last_name=last_name,
            role=role,
            bio=bio,
        )
        session.add(obj)
        await session.flush()
        return obj


    @staticmethod
    async def upsert_by_username(
        session: AsyncSession,
        *,
        user_name: str,
        first_name: str,
        last_name: str,
    ) -> Member:

        res = await session.execute(select(Member).where(Member.user_name == user_name))
        obj = res.scalar_one_or_none()
        if obj is None:
            obj = Member(
                user_name=user_name,
                first_name=first_name,
                last_name=last_name,
                role=MemberRole.member,
                bio="",
            )
            session.add(obj)
        else:
            obj.first_name = first_name
            obj.last_name = last_name
        await session.flush()
        return obj


    @staticmethod
    async def update_bio(session: AsyncSession, member: Member, bio: str) -> None:
        member.bio = bio


    @staticmethod
    async def delete_by_id(session: AsyncSession, member_id: UUID) -> None:
        await session.execute(delete(Member).where(Member.id == member_id))


class ApplicationDAO:
    @staticmethod
    async def get_pending_by_tg_user_id(
        session: AsyncSession,
        tg_user_id: int,
    ) -> Optional[Application]:
        res = await session.execute(
            select(Application).where(
                Application.tg_user_id == tg_user_id,
                Application.status == ApplicationStatus.pending,
            )
        )
        return res.scalar_one_or_none()


    @staticmethod
    async def create(session: AsyncSession, *, tg_user_id: int) -> Application:
        app = Application(tg_user_id=tg_user_id, status=ApplicationStatus.pending)
        session.add(app)
        await session.flush()
        return app


    @staticmethod
    async def mark_approved(
        session: AsyncSession,
        app: Application,
        *,
        invite_id: UUID,
    ) -> None:
        app.status = ApplicationStatus.approved
        app.invite_id = invite_id


    @staticmethod
    async def remove_all_for_tg_user(session: AsyncSession, tg_user_id: int) -> None:
        await session.execute(delete(Application).where(Application.tg_user_id == tg_user_id))


class InviteDAO:
    @staticmethod
    async def get_by_link(session: AsyncSession, invite_link: str) -> Optional[Invite]:
        res = await session.execute(select(Invite).where(Invite.invite_link == invite_link))
        return res.scalar_one_or_none()


    @staticmethod
    async def create(
        session: AsyncSession,
        *,
        chat_id: int,
        intended_user_id: int,
        invite_link: str,
        expire_at_unix: int,
        member_limit: int = 1,
        creates_join_request: bool = True,
    ) -> Invite:

        inv = Invite(
            chat_id=chat_id,
            invite_link=invite_link,
            intended_user_id=intended_user_id,
            expire_at=expire_at_unix,  # BIGINT (unix ts)
            member_limit=member_limit,
            creates_join_request=creates_join_request,
            is_revoked=False,
        )
        session.add(inv)
        await session.flush()
        return inv


    @staticmethod
    async def revoke(session: AsyncSession, invite: Invite) -> None:
        invite.is_revoked = True



