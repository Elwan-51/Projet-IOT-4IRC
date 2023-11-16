from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic import BaseModel
from sqlalchemy import Column, Float, String, Integer, DateTime, Boolean
from sqlalchemy.orm import Session
import hashlib
from app.dependencies import config
import random


SQLALCHEMY_DATABASE_URL = f'{config["DATABASE"]["DATABASE_TYPE"]}://{config["DATABASE"]["USER"]}:{config["DATABASE"]["PASSWORD"]}@{config["DATABASE"]["URL"]}:{config["DATABASE"]["PORT"]}/{config["DATABASE"]["DATABASE"]}'
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DBValue(Base):
    __tablename__ = 'value'
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(10))
    time = Column(DateTime)
    value = Column(Float)


class DBUser(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(50), unique=True)
    password = Column(String(250))
    disable = Column(Boolean)
    token = Column(String(250))


Base.metadata.create_all(bind=engine)


class Value(BaseModel):
    value: float


class ValueInDB(BaseModel):
    id: Optional[int] = None
    type: Optional[str] = None
    value: float
    time: Optional[datetime] = datetime.now()

    class Config:
        from_attributes = True


class User(BaseModel):
    login: str
    disable: Optional[bool] = False


class UserInDB(User):
    password: str
    id: Optional[int] = None
    token: Optional[str] = None

    class Config:
        from_attributes = True


def get_data_id(db: Session, value_id: int):
    return db.query(DBValue).where(DBValue.id == value_id).first()


def get_data(db: Session):
    return db.query(DBValue).all()


def get_types(db: Session, value_type: str):
    return db.query(DBValue).where(DBValue.type == value_type).all()


def get_last_types(db: Session, value_type: str):
    return  db.query(DBValue).order_by(DBValue.id.desc()).where(DBValue.type == value_type).first()


def create_data(db: Session, value: Value):
    db_value = DBValue(**value.model_dump())
    db.add(db_value)
    db.commit()
    db.refresh(db_value)

    return db_value


def create_user(db: Session, user: UserInDB):
    user.password = hashlib.sha256(user.password.encode()).hexdigest()
    user.token = hashlib.sha256(f'{user.login}{datetime.now()}'.encode()).hexdigest()
    db_user = DBUser(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session):
    return db.query(DBUser).all()


def get_user_name(db: Session, user_name: str):
    return  db.query(DBUser).where(DBUser.login == user_name).first()

def get_user_by_token(db: Session, token: str):
    return db.query(DBUser).where(DBUser.token == token).first()