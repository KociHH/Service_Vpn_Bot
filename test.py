import random
from collections import defaultdict

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import  AsyncSession

from bd_api.middle import async_session
from bd_api.middlewares.sa_tables import User


async def test(db_session: AsyncSession):
    results = await db_session.execute(select(User.admin_status, User.user_name))

    res = results.all()
    for user_name, admin_status in res:
        print(user_name, admin_status)


async def main():
    async with async_session() as session:
        await test(session)


asyncio.run(main())