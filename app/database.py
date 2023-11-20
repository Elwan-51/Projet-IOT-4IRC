# Import required libraries
from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic import BaseModel
from sqlalchemy import Column, Float, String, Integer, DateTime, Boolean
from sqlalchemy.orm import Session
import hashlib
from app.dependencies import config

# Construct the database URL using configuration values
SQLALCHEMY_DATABASE_URL = f'{config["DATABASE"]["DATABASE_TYPE"]}://{config["DATABASE"]["USER"]}:{config["DATABASE"]["PASSWORD"]}@{config["DATABASE"]["URL"]}:{config["DATABASE"]["PORT"]}/{config["DATABASE"]["DATABASE"]}'
# Create the engine for database connection
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
# Create a session that will be used to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Create a base class for declarative models
Base = declarative_base()

# Define a function to get a database session
def get_db():
    # function used to connect to the database
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define a model for the "value" table in the database
class DBValue(Base):
    # Table Value
    __tablename__ = 'value'
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(10))
    time = Column(DateTime)
    value = Column(Float)

# Define a model for the "user" table in the database
class DBUser(Base):
    # Table User
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(50), unique=True)
    password = Column(String(250))
    disable = Column(Boolean)
    token = Column(String(250))

# Create the tables in the database
Base.metadata.create_all(bind=engine)

# Define a model for a new value
class Value(BaseModel):
    value: float

# Define a model for a value in the database
class ValueInDB(BaseModel):

    id: Optional[int] = None
    type: Optional[str] = None
    value: float
    time: Optional[datetime] = datetime.now()

    class Config:
        from_attributes = True

# Define a base model for a user
class User(BaseModel):
    login: str
    disable: Optional[bool] = False

# Define a model for a user in the database
class UserInDB(User):
    # User model in DataBase
    password: str
    id: Optional[int] = None
    token: Optional[str] = None


    class Config:
        from_attributes = True

# Define functions for interacting with the database

# Get data by id
def get_data_id(db: Session, value_id: int):
    # get the data based on the data id
    return db.query(DBValue).where(DBValue.id == value_id).first()

# Get all data
def get_data(db: Session):
    # get all data
    return db.query(DBValue).all()

# Get data of a specific type
def get_types(db: Session, value_type: str):
    # get all data of a given type
    return db.query(DBValue).where(DBValue.type == value_type).all()

# Get last data for a specific type
def get_last_types(db: Session, value_type: str):
    return db.query(DBValue).order_by(DBValue.id.desc()).where(DBValue.type == value_type).first()


# Create a new data
def create_data(db: Session, value: Value):
    # Create a new data
    db_value = DBValue(**value.model_dump())
    db.add(db_value)
    db.commit()
    db.refresh(db_value)
    return db_value

# Create a new user
def create_user(db: Session, user: UserInDB):
    # Create a new user
    user.password = hashlib.sha256(user.password.encode()).hexdigest()
    user.token = hashlib.sha256(f'{user.login}{datetime.now()}'.encode()).hexdigest()
    db_user = DBUser(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Get all users
def get_users(db: Session):
    # get all users
    return db.query(DBUser).all()

# Get a user by name
def get_user_name(db: Session, user_name: str):
    return db.query(DBUser).where(DBUser.login == user_name).first()

# Get a user by token
def get_user_by_token(db: Session, token: str):
    return db.query(DBUser).where(DBUser.token == token).first()

