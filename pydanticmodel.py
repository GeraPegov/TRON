from pydantic import BaseModel
from datetime import datetime, time, date
from pydantic import field_validator
from fastapi import HTTPException
import re


class User(BaseModel):
    data: date
    time: time
    ip: str

    @field_validator('ip')
    def check(cls, value):
        if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', value):
            raise HTTPException(status_code=400, detail="Некорректный IP")
        octets = value.split('.')
        for octet in octets:
            num = int(octet)
            if num < 0 or num > 255:
                raise HTTPException(status_code=400, detail="Некорректный IP")
        return value


class WalletRequest(BaseModel):
    user_wallet: str
    
    @field_validator('user_wallet')
    def check(cls, value):
        if len(value) != 34:
            raise HTTPException(status_code=400, detail='wrong wallet')
        return value
    
class Showdb(BaseModel):
    ip: str
    data: date
    time: time
    user_wallet: str 
