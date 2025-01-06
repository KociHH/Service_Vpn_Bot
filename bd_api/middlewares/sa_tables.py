import asyncio
import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, BIGINT, BigInteger, Date, Float, ForeignKey, func
from sqlalchemy.testing.plugin.plugin_base import logging

from bd_api.middle import engine, logger

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True,)
    user_id = Column(BigInteger, unique=True, nullable=False)
    user_name = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    admin_status = Column(String, nullable=False, default='user')



class Subscribers(Base):
    __tablename__ = "subscribers"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    month = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False, default=func.now())
    end_date = Column(Date, nullable=False)
    status = Column(String, nullable=False, default="active")


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


# class subcriber():
#     def __init__(self, user: Subscribers, month: int, data: dict, start_date: datetime.date, end_date: datetime.date):
#         self.user = user
#         self.month = month
#         self.data = data
#         self.start_date = start_date
#         self.end_date = end_date
#
#     def Update_Subscribers(self):
#         pass
#
#
#     def month_time(self):
#
#         if self.month == self.data["month: 1"]:
#             duration = 30
#         elif self.month == self.data["month: 2"]:
#             duration = 60
#         elif self.month == self.data["month: 3"]:
#             duration = 90
#         else:
#             logger.error('Неизвестная дата')
#         return int(duration)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(create_tables())
