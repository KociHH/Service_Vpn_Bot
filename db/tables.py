import asyncio
from datetime import datetime, timedelta
import pytz
from sqlalchemy import select, LargeBinary
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, func, DateTime, Boolean
from sqlalchemy import  pool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from utils.work import url_db, currently_msk
import logging
from kos_Htools.sql.sql_alchemy.dao import BaseDAO

logger = logging.getLogger(__name__)

engine = create_async_engine(
    url_db, 
    future=True, 
    echo=False, 
    poolclass=pool.NullPool, 
)
async_session = async_sessionmaker(engine, expire_on_commit=False,  class_=AsyncSession)

Base = declarative_base()

class Images(Base):
    __tablename__ = 'images'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    image = Column(LargeBinary, nullable=False)
    name = Column(String, nullable=True)

class User(Base):
    """
    user_id: int
    user_name: str | None
    full_name: str | None
    admin_status: str = 'user'
    """
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    user_name = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    admin_status = Column(String, nullable=False, default='user')

class Subscription(Base):
    """
    user_id: int
    start_date: datetime
    end_date: datetime
    status: str
    """
    __tablename__ = "subscribers"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False, unique=True)
    start_date = Column(DateTime, nullable=False, default=func.now())
    end_date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default="not active")

class TrialSubscription(Base):
    """
    user_id: int
    start_date: datetime
    end_date: datetime
    status: str
    """
    __tablename__ = "trial_subscribers"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False, unique=True)
    start_date = Column(DateTime, nullable=False, default=func.now())
    end_date = Column(DateTime, nullable=False)
    trial_used = Column(Boolean, nullable=False, default=False)

class VlessLinks(Base):
    __tablename__ = "vless_links"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    src = Column(String, nullable=False)
    add_att = Column(DateTime, nullable=False)


class PaymentHistory(Base):
    """
    user_id: int
    month: int
    date_paid: datetime
    payment_amount: int
    """
    # множество
    __tablename__ = "payment_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    month = Column(Integer, nullable=False)
    date_paid = Column(DateTime, nullable=False)
    payment_amount = Column(BigInteger, nullable=False) # в рублях без копеек

class subscriber:
    def __init__(
            self, 
            user_id: int, 
            month: int, 
            db_session: AsyncSession
            ):
        self.user_id = user_id
        self.month = month
        self.sub_dao = BaseDAO(Subscription, db_session)


    def month_time(self, month: int) -> int:
        if month in [1, 3, 6]:
            return month * 30
        else:
            logger.error(f"Неизвестное значение месяца: {month}")
            raise ValueError("Неизвестное значение месяца.")


    async def date_Subscribers(self):
        try:
            month_days = self.month_time(self.month)
        except ValueError: 
            return

        current_date = currently_msk()
        new_end_date = current_date + timedelta(days=month_days)

        existing_subscription = await self.sub_dao.get_one(Subscription.user_id == self.user_id)

        if existing_subscription:
            old_end_date = existing_subscription.end_date
            update_sub = await self.sub_dao.update(
                Subscription.user_id == self.user_id,
                {
                    "start_date": existing_subscription.start_date,
                    "end_date": new_end_date if old_end_date <= current_date else old_end_date + timedelta(days=month_days),
                    "status": "active",
                }
            )
            if not update_sub:
                logger.error(f"Юзер {self.user_id} не был обновлен в базе {self.sub_dao.model.__name__}")
                return

            logger.info(
                f"Продлеваем/активируем подписку для пользователя {self.user_id}. "
                f"Новая дата окончания: {new_end_date}"
            )

        else:
            new_subscription  = await self.sub_dao.create({
                "user_id": self.user_id,
                "start_date": current_date,
                "end_date": new_end_date,
                "status": "active",
            })
            if not new_subscription:
                logger.error(f"Юзер {self.user_id} не был добавлен в базу {self.sub_dao.model.__name__}")
                return

            logger.info(f"Создана новая подписка для пользователя {self.user_id}, срок: {month_days} дней.")

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
