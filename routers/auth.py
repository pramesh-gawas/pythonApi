from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException,Request
from pydantic import BaseModel
from todoApp.models import Users
from passlib.context import CryptContext
from todoApp.database import sessionmaker
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt    
from datetime import timedelta,datetime, timezone
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os
load_dotenv()
ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

becrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")
templates = Jinja2Templates(directory="todoApp/templates")

#pages


@router.get("/login-page",status_code=status.HTTP_200_OK)
def login_page(request:Request):
    return templates.TemplateResponse("login.html",{"request":request})

@router.get("/register-page",status_code=status.HTTP_200_OK)
def register_page(request:Request):
    return templates.TemplateResponse("register.html",{"request":request})

### endpoints

class CreateUserRequest(BaseModel):
    username: str
    password: str
    last_name: str
    first_name: str
    email: str
    role: str 
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
def get_db():
    db = sessionmaker()
    try:
        yield db
    finally:
        db.close()
        
def create_access_token(usename: str,user_id: int,role:str,expires_delta:timedelta):
    to_encode = {"sub":usename,"id":user_id,"role":role}
    expires_delta = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp":expires_delta})
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token:Annotated[str,Depends(oauth_bearer)],db:Annotated[Session,Depends(get_db)]):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials") 
            return  {"username":username,"id":user_id,"role":user_role}
    except jwt.JWTError:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials") 
    user = db.query(Users).filter(Users.id == user_id).first()
    if user is None:
         raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials") 
    return user

def authenticate_user(username:str,password:str,db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not becrypt_context.verify(password, user.hashed_password):
        return False
    return user


@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_user(db:Annotated[Session, Depends(get_db)], create_user_request: CreateUserRequest):
  
    create_user_model = Users(
        username=create_user_request.username,
        email=create_user_request.email,
    first_name=create_user_request.first_name,
    last_name=create_user_request.last_name,role=create_user_request.role,
    hashed_password = becrypt_context.hash(create_user_request.password))

    db.add(create_user_model)
    db.commit()
    
    
@router.post("/token",response_model=Token)
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],db:Annotated[Session,Depends(get_db)]):
    
    user = authenticate_user(form_data.username,form_data.password,db)
    if not user:
         raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials") 
    token = create_access_token(user.username,user.id,user.role,timedelta(minutes=20))
    return {"access_token":token,"token_type":"bearer"}

