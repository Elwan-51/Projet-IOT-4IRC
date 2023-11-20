# Router for global data manipulation
from app.database import get_db, get_data_id, get_data, get_last_types
from app.database import List, Session, ValueInDB
from fastapi import APIRouter, Depends

# Router configuration
router = APIRouter(
    prefix='/data',
    tags=['Global Data Manipulation'],
    responses={404: {"description": "Not found"}}
)


@router.get('/{data_id}', response_model=ValueInDB)
def get_data_by_id_view(data_id: int, db: Session = Depends(get_db)) -> ValueInDB:
    # get data by id
    return get_data_id(db, data_id)


@router.get('/', response_model=list[ValueInDB])
def get_all_data_view(db: Session = Depends(get_db)) -> ValueInDB:
    # get all data
    return get_data(db)


@router.get('/last/', response_model=List[ValueInDB])
def get_last_datas_view(db: Session = Depends(get_db)) -> List[ValueInDB]:
    # return last luminosity and last temperature

    data = [
        get_last_types(db, 'lumi'),
        get_last_types(db, 'temp')
    ]
    return data
