from app.database import Value, Session, List, ValueInDB
from app.database import get_db, create_data, get_types, get_last_types
from fastapi import APIRouter, Depends
from app.dependencies import oauth2_scheme
from typing import Annotated
router = APIRouter(
    prefix='/lumi',
    tags=['Light Level'],
    responses={404: {"description": "Not found"}}
)


@router.post('/', response_model=Value)
def create_lumi_entry(lumi: Value,token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    lumi = ValueInDB(**lumi.dict())
    lumi.type = "lumi"
    db_value = create_data(db, lumi)
    return db_value

@router.get('/', response_model=List[ValueInDB])
def get_all_lumi_view(db: Session = Depends(get_db)):
    return get_types(db, "lumi")

@router.get('/last/', response_model=ValueInDB)
def get_last_lumi_view(db: Session = Depends(get_db)):
    return get_last_types(db, 'lumi')