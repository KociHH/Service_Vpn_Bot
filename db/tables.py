import asyncio
from datetime import datetime, timedelta
import pytz
from alembic.util import status
from sqlalchemy import select, LargeBinary
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, BIGINT, BigInteger, Date, Float, ForeignKey, func
from db.middlewares.middle import async_session
from db.middlewares.middle import engine, logger
from utils.other import currently_msk
from kos_Htools.sql.sql_alchemy.dao import BaseDAO

Base = declarative_base()

class Images(Base):
    __tablename__ = 'images'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    image = Column(LargeBinary, nullable=False)
    name = Column(String, nullable=True)

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    user_name = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    admin_status = Column(String, nullable=False, default='user')

class Subscription(Base):
    __tablename__ = "subscribers"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False, unique=True)
    month = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False, default=func.now())
    end_date = Column(Date, nullable=False)
    status = Column(String, nullable=False, default="not active")

class PaidSubscribers(Base):
    # множество
    __tablename__ = "paid_subscribers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    date_paid = Column(Date, nullable=False)
    payment_amount = Column(BigInteger, nullable=False) # в рублях без копеек

user_dao = BaseDAO(User, async_session)
images_dao = BaseDAO(Images, async_session)
sub_dao = BaseDAO(Subscription, async_session)
paid_dao = BaseDAO(PaidSubscribers, async_session)

class subscriber:
    def __init__(self, user_id: int, month: int, start_date: datetime.date, end_date: datetime.date):
        self.user_id = user_id
        self.month = month
        self.start_date = start_date
        self.end_date = end_date


    def month_time(self, month):
        try:
            if month == 1:
                return month * 30
            elif month == 3:
                return month * 30
            elif month == 6:
                return month * 30
            else:
                raise ValueError("Неизвестное значение месяца.")
        except Exception as e:
            logger.error(e)


    async def date_Subscribers(self):
        month_days = self.month_time(self.month)
        if month_days == 0:
            return

        current_date = currently_msk.date()
        new_end_date = current_date + timedelta(days=month_days)

        existing_subscription = await sub_dao.get_one((
                Subscription.user_id == self.user_id,
                Subscription.end_date >= current_date
            ))

        if existing_subscription and existing_subscription.end_date >= current_date:

            existing_subscription.end_date += timedelta(days=month_days)
            existing_subscription.start_date = current_date
            logger.info(
                f"Продлеваем подписку для пользователя {self.user_id}. "
                f"Новая дата окончания: {existing_subscription.end_date}"
            )

        else:
            new_subscription  = sub_dao.create({
                "user_id": self.user_id,
                "month": self.month,
                "start_date": current_date,
                "end_date": new_end_date,
                "status": "active",
            })
            if not new_subscription:
                logger.error(f"Юзер {self.user_id} не был добавлен в подписки")
                return

            logger.info(f"Создана новая подписка для пользователя {self.user_id}, срок: {month_days} дней.")


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
