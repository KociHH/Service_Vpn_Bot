import asyncio
from datetime import datetime, timedelta
import pytz
from alembic.util import status
from sqlalchemy import select, LargeBinary
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, BIGINT, BigInteger, Date, Float, ForeignKey, func

from bd_api.middle import engine, logger
from utils.date_moscow import get_current_date

Base = declarative_base()

class Images(Base):
    __tablename__ = 'images'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    id_image = Column(BigInteger, nullable=False, unique=True)
    image = Column(LargeBinary, nullable=False)
    name = Column(String, nullable=True)

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True,)
    user_id = Column(BigInteger, unique=True, nullable=False)
    user_name = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    admin_status = Column(String, nullable=False, default='user')


class Subscription(Base):
    __tablename__ = "subscribers"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    month = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False, default=func.now())
    end_date = Column(Date, nullable=False)
    status = Column(String, nullable=False, default="not active")


class UserUpdater:
    def __init__(self, user: User | Subscription, new_data: dict):
        self.user = user
        self.new_data = new_data

    def update(self):

        for key, value in self.new_data.items():
            if hasattr(self.user, key) and getattr(self.user, key) != value:
                setattr(self.user, key, value)

    async def save_to_db(self, db_session: AsyncSession):
        try:
            self.update()
            db_session.add(self.user)
            await db_session.commit()
        except Exception as e:
            await db_session.rollback()
            raise RuntimeError(f"Ошибка сохранения пользователя в базу данных: {e}")


class subscriber():
    def __init__(self, user_id: int, month: int, start_date: datetime.date, end_date: datetime.date):
        self.user_id = user_id
        self.month = month
        self.start_date = start_date
        self.end_date = end_date


    def month_time(self, month):
        try:
            if month == 1:
                return 30
            elif month == 2:
                return 60
            elif month == 3:
                return 90
            else:
                raise ValueError("Неизвестное значение месяца.")
        except Exception as e:
            logger.error(e)


    async def date_Subscribers(self, db_session: AsyncSession):
        month_days = self.month_time(self.month)
        if month_days == 0:
            return

        current_date = get_current_date(True)
        new_end_date = current_date + timedelta(days=month_days)

        result = await db_session.execute(
            select(Subscription).where(
                Subscription.user_id == self.user_id,
                Subscription.end_date >= current_date
            )
        )
        existing_subscription = result.scalars().first()

        if existing_subscription and existing_subscription.end_date >= current_date:

            existing_subscription.end_date += timedelta(days=month_days)
            existing_subscription.start_date = current_date
            db_session.add(existing_subscription)
            await db_session.commit()
            logger.info(
                f"Продлеваем подписку для пользователя {self.user_id}. "
                f"Новая дата окончания: {existing_subscription.end_date}"
            )

        else:
            new_subscription  = Subscription(
                user_id=self.user_id,
                month=self.month,
                start_date=current_date,
                end_date=new_end_date,
                status="active",
            )
            db_session.add(new_subscription)
            await db_session.commit()
            logger.info(f"Создана новая подписка для пользователя {self.user_id}, срок: {month_days} дней.")


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
