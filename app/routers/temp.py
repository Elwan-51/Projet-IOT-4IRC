from database import Value, Session, List
from database import get_db, get_last_types, get_types, create_data
from fastapi import APIRouter, Depends
from typing import Annotated
from dependencies import oauth2_scheme

router = APIRouter(
    prefix='/temp',
    tags=['Temperatures'],
    responses={404: {"description": "Not found"}}
)

@router.post('/', response_model=Value)
def create_temp_entry(temp: Value,token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    temp.type = "temp"
    db_value = create_data(db, temp)
    return db_value


@router.get('/', response_model=List[Value])
def get_all_temp_view(db: Session = Depends(get_db)):
    return get_types(db, "temp")


@router.get('/last/')
def get_last_lumi_view(db: Session = Depends(get_db)):
    return get_last_types(db, 'temp')