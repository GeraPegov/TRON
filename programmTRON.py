from requests import HTTPError
from fastapi import FastAPI, Depends, Request, HTTPException, Form
from sqlalchemy import  select, desc, delete
from typing import Dict
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from DBmodels import Base, Wallet
from database import engine, get_db, AsyncSessionLocal
from pydanticmodel import  WalletRequest, User, Showdb
from datetime import datetime, timedelta
import logging
from log import start_logging
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
import httpx

templates = Jinja2Templates(directory='templates')

start_logging()
logger = logging.getLogger(__name__)
logging.getLogger('sqlalchemy').propagate = False

#Передача в ядро всех моделей от Base 
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

#Функция для очистки данных из таблицы 
async def clear_db():
    async with AsyncSessionLocal() as session:
        logger.info(f'start clear_db')
        data = delete(Wallet).where((Wallet.time + timedelta(hours=24)) < datetime.now().time())
        logger.info(f'{datetime.now().time()}')
        await session.execute(data)
        await session.commit()

scheduler = AsyncIOScheduler()
#Планировщик который вызывает функцию clear_db каждые 24 часа
def plan_clear():
    logger.info(f'start plan_clear')
    scheduler.add_job(clear_db, 'interval', hours=24)
    scheduler.start()
#Инициализирует планировщик перед запуском программы и передачи метаданных в ядро
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f'start lifespan')
    await init_db()
    plan_clear()
    yield
    await engine.dispose()
    scheduler.shutdown()

app=FastAPI(lifespan=lifespan)
    
def searchip(request: Request):
    """
    Вынимает из Request айпи клиента
    """
    if 'x_forwarded_for' in request.headers:
        return request.headers['x_forwarded_for'].split(",")[0].strip()
    return request.client.host

@app.get('/', response_class=HTMLResponse)
async def start(request: Request):
    """
    Грузит HTML на главную веб-страницу
    """
    logger.info('Start work "/" HTML code')
    return templates.TemplateResponse('form.html', {'request': request})

@app.post('/wallet', response_class=JSONResponse)
async def first_get_db(
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
        user = User(ip=ip_client, data=data, time=time)
        try:
            logger.info(f'Open db for Post/wallet')
            db_user = Wallet(namewallet=address_wallet, data=user.data, time=user.time, ip=user.ip)
            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)
            await session.close()
            logger.info(f'Close db for Post/wallet')
        except SQLAlchemyError as e:
            logger.error(f'SQLAlchemy error: {str(e)}')
            raise HTTPException(status_code=400, detail='Ошибка данных')
        
        #API для получения информации от TRON 
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = "https://api.shasta.trongrid.io/wallet/getaccountresource"
                payload = {
                    "address": address_wallet,
                    "visible": True
                }
                headers = {
                    "accept": "application/json",
                    "content-type": "application/json"
                }

                response = await client.post(url, json=payload, headers=headers)
                return response.json()
        except HTTPError as e:
            raise HTTPException(status_code=400, detail='Ошибка на стороне Tron, повторите попытку позднее')
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
    
@app.get('/show')
async def showdb(session: AsyncSession = Depends(get_db)) -> Dict:
    """
    Вывод последних 5 записей из таблицы и преобразование каждого класса model.Wallet, из которых состоят записи в БД,
    в тип dict
    """
    try:
        logger.info('Start /show')
        #Сортирую по убыванию ID с лимитом в 5 записей
        show_datadb = select(Wallet).order_by(desc(Wallet.id)).limit(5)
        results = await session.execute(show_datadb)
        active_users = results.scalars().all()
        await session.close()
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
        logger.info(f'Warning get/show: {e} ')
        raise HTTPException(status_code=400, detail='Ошибка базы данных')
    

