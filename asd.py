from pydanticmodel import Showdb
from datetime import date, time
from DBmodels import Wallet, Base
from database import AsyncSessionLocal, engine
from sqlalchemy import  select


examples_wallet='TZ4UXDV5ZhNW7fb2AMSbgfAEZ7hWsnYS2g'
examples_ip = "12.32.0.1"
examples_data = date(2025, 4, 22)
examples_time = time(9, 37, 54, 166071)
examples_id = 1
class Active:
    def __init__(self):
        self.id = 1
        self.data = examples_data
        self.time = examples_time
        self.ip = examples_ip
        self.namewallet = examples_wallet
active_user = Active()
active_users = [active_user]

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
async def test_bd():
    async with AsyncSessionLocal() as session:
        add = Wallet(namewallet=examples_wallet, data=examples_data, time=examples_time, ip=examples_ip)
        session.add(add)
        await session.commit()
        await session.refresh(add)
        show = select(Wallet).where(Wallet.ip==examples_ip)
        result = await session.execute(show)
        result_db = result.scalars().all()
        dict_show = {}
        for i in range(len(active_users)):
            dict_show['qwe'] = Showdb(
                ip=result_db[i].ip, 
                data=result_db[i].data,
                time=result_db[i].time,
                user_wallet=result_db[i].namewallet
                )
        # return result_db
        return result_db

a = test_bd()
print(a)
