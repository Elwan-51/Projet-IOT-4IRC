import hashlib
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from app.database import get_user_name, Session, get_db
from app.routers import lumi
from app.routers import temp
from app.routers import data
from app.routers import user

app = FastAPI() # Fast API app
# Importer router
app.include_router(lumi.router)
app.include_router(temp.router)
app.include_router(data.router)
app.include_router(user.router)


@app.get("/")
async def root():
    return {"message": "Doc available at url/docs"}


@app.post('/token')
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    # Get token for auth
    user_db = get_user_name(db, form_data.username)
    print(form_data.username)
    if not user_db:
        raise HTTPException(status_code=400, detail="Incorect username or Password")
    hashed_password = hashlib.sha256(form_data.password.encode()).hexdigest()
    if not hashed_password == user_db.password:
        raise HTTPException(status_code=400, detail="Incorect username or Password")
    return {"access_token": user_db.token, "token_type": "bearer"}
