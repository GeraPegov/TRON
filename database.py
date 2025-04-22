from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError, OperationalError, InterfaceError, ProgrammingError, DataError, NoResultFound
from fastapi import HTTPException
from contextlib import asynccontextmanager




SQL_DB_URL = 'sqlite+aiosqlite:///tron.db'

engine = create_async_engine(SQL_DB_URL, connect_args={'check_same_thread': False}, echo=True, pool_pre_ping=True)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)

Base = declarative_base()

@asynccontextmanager
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except NoResultFound as e:
            raise HTTPException(status_code=404, detail="Запись не найдена")
        except (ProgrammingError, DataError) as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail='Ошибка запроса')
        except (OperationalError, InterfaceError) as e:
            raise HTTPException(status_code=503, detail='Сервис временно недоступен. Попробуйте позже')
        except SQLAlchemyError as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail="Ошибка сервера")
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Неожиданная ошибка {str(e)}"
            )
        finally:
            await session.close()





