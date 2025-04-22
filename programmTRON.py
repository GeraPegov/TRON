import requests
from requests import HTTPError
from fastapi import FastAPI, Depends, Request, HTTPException, Form
from sqlalchemy import  select, desc, delete
from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from DBmodels import Base, Wallet
from database import engine, get_db
from pydanticmodel import  WalletRequest, User, Showdb
from datetime import datetime, timedelta
import logging
from log import start_logging
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager

templates = Jinja2Templates(directory='templates')

start_logging()
logger = logging.getLogger(__name__)
logging.getLogger('sqlalchemy').propagate = False


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all(bind=engine))

def clear_db():
    
    with Session(get_db()) as ses:
        data = delete(Wallet).where(Wallet.data < (Wallet.data + timedelta(days=1)))
        ses.execute(data)
        ses.commit()

scheduler = BackgroundScheduler()

def plan_clear():
    scheduler.add_job(clear_db, 'interval', hours=24)
    scheduler.start()

@asynccontextmanager
async def lifespan(app: FastAPI):
    plan_clear()
    yield

app=FastAPI(lifespan=lifespan)
    


#Функция для IP клиента
def searchip(request: Request):
    """
    Вынимает из Request айпи клиента
    """
    if 'x_forwarded_for' in request.headers:
        return request.headers['x_forwarded_for'].split(",")[0].strip()
    return request.client.host

#Страница с HTML кодом
@app.get('/', response_class=HTMLResponse)
async def start(request: Request):
    """
    Грузит HTML на главную страницу
    """
    logger.info('Start work "/" HTML code')
    return templates.TemplateResponse('form.html', {'request': request})

#Сохранение информации в БД и выдача информации по кошельку
@app.post('/wallet', response_class=JSONResponse)
async def get_db(
    user_wallet: WalletRequest = Form(...),
    session: AsyncSession = Depends(get_db), 
    request: Request = None
    ) -> Dict:
    """
    Получение номера кошелька, IP адреса, занесение данных в БД вместе с датой
    и ответ сервера о состоянии кошелька в формате json
    """
    logger.info(f'Start work /wallet')
    try:
        address_wallet = user_wallet.user_wallet
        ip_client = searchip(request)
        data_time = datetime.now()
        data = data_time.date()
        time = data_time.time().replace(microsecond=0)
        logger.info(f'time {time} data {data}')
        user = User(ip=ip_client, data=data, time=time)
        #Проверка валидации 
        async with get_db() as session:
            logger.info(f'Open db for Post/wallet')
            db_user = Wallet(namewallet=address_wallet, data=user.data, time=user.time, ip=user.ip)
            #Добавление в БД
            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)
            logger.info(f'Close db for Post/wallet')
            #API для получения информации от TRON 
            url = "https://api.shasta.trongrid.io/wallet/getaccountresource"
            payload = {
                "address": address_wallet,
                "visible": True
            }
            headers = {
                "accept": "application/json",
                "content-type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers)
            return response.json()
    except HTTPError as e:
        logger.warning(f'Mistake validate: {str(e)}')
        raise HTTPException(status_code=422, detail="Ошибка обработки данных")
    except ValueError as e:
        logger.warning(f'Mistake value: {str(e)}')
        raise HTTPException(status_code=400, detail="Неправильный запрос")
    except (ConnectionError, TimeoutError) as e:
        logger.warning(f'Connection Error: {str(e)}')
        raise HTTPException(status_code=500, detail="Нет доступа на стороне TRON")
    except Exception as e:
        logger.warning(f'Error Exception: {str(e)}')
        raise HTTPException(status_code=404, detail="Неизвестная ошибка")
    
#Просмотр последних активностей
@app.get('/show')
async def showdb(session: AsyncSession = Depends(get_db)) -> Dict:
    """
    Вывод последних 5 записей из таблицы и преобразование каждого класса model.Wallet, из которых состоят записи в БД,
    в тип dict
    """
    try:
        async with get_db() as session:
            logger.info('Start /show')
            show_datadb = select(Wallet).order_by(desc(Wallet.id)).limit(5)
            results = await session.execute(show_datadb)
            active_users = results.scalars().all()
            dict_show = {}
            for i in range(len(active_users)):
                dict_show[active_users[i].id] = Showdb(
                    ip=active_users[i].ip, 
                    data=active_users[i].data,
                    time=active_users[i].time,
                    user_wallet=active_users[i].namewallet
                    )
            return dict_show
    except Exception as e:
        HTTPException(status_code=400, detail='Error')
    