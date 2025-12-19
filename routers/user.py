


from fastapi import APIRouter,Depends,Path,HTTPException
from typing import Annotated
from pydantic import BaseModel,Field
from models import Users
from sqlalchemy.orm import Session
from database import sessionmaker as SessionLocal
from starlette import status
from passlib.context import CryptContext
from routers.auth import get_current_user

router = APIRouter(
    prefix="/user",
    tags=["user"]
)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
class userVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)
        
        
user_dependency = Annotated[dict,Depends(get_current_user)]
db_dependency = Annotated[Session,Depends(get_db)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/",status_code=status.HTTP_200_OK)
def get_user(user:user_dependency, db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_detail = db.query(Users).filter(Users.id == user.id).first()
    return user_detail


@router.put("/password",status_code=status.HTTP_200_OK)
async def change_password( user:user_dependency, db:db_dependency,user_verfication:userVerification):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    item = db.query(Users).filter(Users.id == user.id).first()
    if not bcrypt_context.verify(user_verfication.password,item.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    item.hashed_password = bcrypt_context.hash(user_verfication.new_password)
    db.add(item)
    db.commit()
    db.refresh(item)
    