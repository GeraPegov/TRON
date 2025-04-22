from pydanticmodel import WalletRequest, Showdb, User
from datetime import datetime

examples_request = {
  "host": "127.0.0.1:8000",
}

examples_wallet='TZ4UXDV5ZhNW7fb2AMSbgfAEZ7hWsnYS2g'
examples_ip = "127.0.0.1"
examples_data = datetime(2025, 4, 22)
examples_time = datetime(16, 37, 54, 166071)
examples_id = 1
class Active:
    def __init__(self):
        self.id = 1
        self.data = examples_data
        self.ip = examples_ip
        self.namewallet = examples_wallet
active_user = Active()
active_users = [active_user]



def test_class_walletrequest():
    test_wallet = WalletRequest(user_wallet=examples_wallet)
    assert test_wallet.user_wallet == 'TZ4UXDV5ZhNW7fb2AMSbgfAEZ7hWsnYS2g'

def test_class_showdb():
    test_showdb = Showdb(ip=examples_ip, data=examples_data, user_wallet=examples_wallet)
    assert test_showdb.ip==examples_ip 
    assert test_showdb.data==examples_data
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
            user_wallet=active_users[i].namewallet
            )
    assert dict_show == {1: Showdb(ip="127.0.0.1", data=examples_data, user_wallet='TZ4UXDV5ZhNW7fb2AMSbgfAEZ7hWsnYS2g')}





