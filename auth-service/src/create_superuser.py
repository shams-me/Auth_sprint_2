import asyncio
import logging
import uuid
from logging import config as logging_config

from core.logger import LOGGING
from models.entity import User
from models.role import Role, RoleEnum, UserRoles
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.future import select

logging_config.dictConfig(LOGGING)


async def get_user_by_email(session: AsyncSession, email: str):
    stmt = select(User).where(User.email == email)
    user = await session.execute(stmt)
    return user.scalar_one_or_none()


async def get_role_by_name(session: AsyncSession, name: str):
    stmt = select(Role).where(Role.name == name)
    role = await session.execute(stmt)
    return role.scalar_one_or_none()


async def create_role(session, name):
    session.add(Role(name=name))
    await session.commit()


async def create_superuser(session, email, password, username, role_id):
    user = User(email=email, password=password, username=username, role_id=role_id)
    session.add(user)
    await session.commit()

    user_role = UserRoles(user_id=user.id, role_id=role_id)
    session.add(user_role)
    await session.commit()


async def get_or_create_role(session: AsyncSession, role: RoleEnum) -> Role:
    superuser_role = await get_role_by_name(session, role.value)
    if superuser_role is None:
        await create_role(session, role.value)
        superuser_role = await get_role_by_name(session, role.value)
    return superuser_role


async def get_or_create_superuser(session: AsyncSession, role_id: uuid.UUID):
    superuser = await get_user_by_email(session, settings.super_user_mail)
    if not superuser:
        superuser = await create_superuser(
            session,
            settings.super_user_mail,
            settings.super_user_pass,
            "superuser",
            role_id,
        )
        logging.info("Successfully created Super User")
    else:
        logging.info("Super User already exists")


async def create_super_user(session_maker):
    async with session_maker() as session:
        superuser_role = await get_or_create_role(session, RoleEnum.SUPERUSER)
        await get_or_create_superuser(session, superuser_role.id)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv(".env")
    from core.config import settings

    engine = create_async_engine(settings.construct_sqlalchemy_url())
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    asyncio.run(create_super_user(session_maker))
