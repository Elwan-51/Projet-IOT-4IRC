# Router file for temperature
from app.database import Value, Session, List, ValueInDB
from app.database import get_db, get_last_types, get_types, create_data
from fastapi import APIRouter, Depends
from typing import Annotated
from app.dependencies import oauth2_scheme

# Router configuration
router = APIRouter(
    prefix='/temp',
    tags=['Temperatures'],
    responses={404: {"description": "Not found"}}
)


@router.post('/', response_model=Value)
def create_temp_entry(temp: Value, token: Annotated[str, Depends(oauth2_scheme)],
                      db: Session = Depends(get_db)) -> Value:
    # Create new temperature, require auth
    temp = ValueInDB(**temp.dict())
    temp.type = "temp"
    db_value = create_data(db, temp)
    return db_value


@router.get('/', response_model=List[ValueInDB])
def get_all_temp_view(db: Session = Depends(get_db)) -> List[ValueInDB]:
    # Get all temperature

    return get_types(db, "temp")


@router.get('/last/', response_model=ValueInDB)
def get_last_lumi_view(db: Session = Depends(get_db)) -> ValueInDB:
    # get last temperature
    return get_last_types(db, 'temp')
