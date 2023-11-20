# Contain all route for User
from typing import Annotated
from app.database import User, Session, List, UserInDB
from app.database import get_db, create_user, get_users, get_user_name, get_user_by_token
from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import oauth2_scheme, config

# Router global config
router = APIRouter(
    prefix='/user',
    tags=['User Management'],
    responses={404: {"description": "Not found"}}
)


@router.post('/', response_model=UserInDB)
def create_user_view(user: UserInDB, token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)) -> UserInDB:
    # Create a user, require auth
    db_user = create_user(db, user)
    return db_user


@router.post('/register/', response_model=UserInDB)
def register_user_view(user: UserInDB, db: Session = Depends(get_db)) -> UserInDB:
    # register new user
    db_user = create_user(db, user)
    return db_user


@router.post('/register/', response_model=UserInDB)
def register_user_view(user: UserInDB, db: Session = Depends(get_db)):
    db_user = create_user(db, user)
    return db_user


@router.get('/', response_model=List[User])
def get_all_user_view(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)) -> List[User]:
    # list all user
    return get_users(db)


@router.get('/{user_name}')
def get_user_by_name_view(user_name: str, token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)) -> User:
    # Return user by name
    return get_user_name(db, user_name)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)) -> User:
    # return the current user, require auth
    user = get_user_by_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    # return current_user if user id active
    if current_user.disable:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.get('/me/', response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
    # Return current user
    return current_user


@router.get('/app/', response_model=User)
async def setup_app_user(db: Session = Depends(get_db)) -> User:
    # Create user for the application
    user = UserInDB(login=config['API']['USER'], password=config['API']['PASSWORD'])
    db_user = create_user(db, user)
    return db_user
