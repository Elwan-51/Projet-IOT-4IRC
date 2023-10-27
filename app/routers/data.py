from database import get_db, get_data_id, get_data,get_last_types
from database import List, Value, Session
from fastapi import APIRouter, Depends

router = APIRouter(
    prefix='/data',
    tags=['Global Data Manipulation'],
    responses={404: {"description": "Not found"}}
)

@router.get('/{data_id}')
def get_data_by_id_view(data_id: int, db: Session = Depends(get_db)):
    return get_data_id(db, data_id)


@router.get('/')
def get_all_data_view(db: Session = Depends(get_db)):
    return get_data(db)

@router.get('/last/', response_model=List[Value])
def get_last_datas_view(db: Session = Depends(get_db)):
    data = [
        get_last_types(db, 'lumi'),
        get_last_types(db, 'temp')
    ]
    return data


