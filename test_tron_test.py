from pydanticmodel import WalletRequest, Showdb, User
from datetime import datetime, time, date
from database import engine, get_db, AsyncSessionLocal
from DBmodels import Base, Wallet
from programmTRON import init_db
from sqlalchemy import  select

examples_request = {
  "host": "127.0.0.1:8000",
}

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



def test_class_walletrequest():
    test_wallet = WalletRequest(user_wallet=examples_wallet)
    assert test_wallet.user_wallet == 'TZ4UXDV5ZhNW7fb2AMSbgfAEZ7hWsnYS2g'

def test_class_showdb():
    test_showdb = Showdb(ip=examples_ip, data=examples_data, time=examples_time, user_wallet=examples_wallet)
    assert test_showdb.ip==examples_ip 
    assert test_showdb.data==examples_data
    assert test_showdb.time==examples_time
    assert test_showdb.user_wallet==examples_wallet

def test_class_user():
    testuser = User(data=examples_data, ip=examples_ip, time=examples_time)
    assert testuser.data==examples_data
    assert testuser.time==examples_time
    assert testuser.ip==examples_ip

def test_endpoint_show():
    dict_show = {}
    for i in range(len(active_users)):
        dict_show[active_users[i].id] = Showdb(
            ip=active_users[i].ip, 
            data=active_users[i].data,
            time=active_users[i].time,
            user_wallet=active_users[i].namewallet
            )
    assert dict_show == {1: Showdb(ip=examples_ip, data=examples_data, time=examples_time, user_wallet='TZ4UXDV5ZhNW7fb2AMSbgfAEZ7hWsnYS2g')}

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
        assert dict_show == {'qwe': Showdb(ip=examples_ip, data=examples_data, time=examples_time, user_wallet=examples_wallet)}





