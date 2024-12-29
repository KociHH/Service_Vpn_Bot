import asyncio
import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, BIGINT, BigInteger, Date, Float, ForeignKey

from bd_api.middle import engine

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True,)
    user_id = Column(BigInteger, unique=True, nullable=False)
    user_name = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    admin_status = Column(String, nullable=False, default='user')



class Payment(Base):
    __tablename__ = "payments"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), unique=True,nullable=False,)
    status = Column(String, nullable=False)
    active_data = Column(Date, nullable=False, default='default')
    month = Column(Integer, nullable=True)
    month_two = Column(Integer, nullable=True)
    month_tree = Column(Integer, nullable=True)


class UserUpdater:
    def __init__(self, user: User, new_data: dict):
        self.user = user
        self.new_data = new_data

    def update(self):

        if self.new_data.get("user_id") and self.new_data["user_id"] != self.user.user_id:
            self.user.user_id = self.new_data["user_id"]
        if self.new_data.get("user_name") and self.new_data["user_name"] != self.user.user_name:
            self.user.user_name = self.new_data["user_name"]
        if self.new_data.get("full_name") and self.new_data["full_name"] != self.user.full_name:
            self.user.full_name = self.new_data["full_name"]
        if self.new_data.get("email") and self.new_data["email"] != self.user.email:
            self.user.email = self.new_data["email"]
        if self.new_data.get("admin_status") and self.new_data["admin_status"] != self.user.admin_status:
            self.user.admin_status = self.new_data["admin_status"]

    async def save_to_db(self, db_session: AsyncSession):
        try:
            db_session.add(self.user)
        except Exception as e:
            await db_session.rollback()
            raise RuntimeError(f"Ошибка сохранения пользователя в базу данных: {e}")


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(create_tables())
