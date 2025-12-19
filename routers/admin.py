
from fastapi import APIRouter,Depends,Path,HTTPException
from typing import Annotated
from pydantic import BaseModel,Field
from todoApp.models import TodoItems
from sqlalchemy.orm import Session
from todoApp.database import sessionmaker as SessionLocal
from starlette import status  
from todoApp.routers.auth import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

def get_db():
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
user_dependency = Annotated[dict,Depends(get_current_user)]
db_dependency = Annotated[Session,Depends(get_db)]


@router.get("/todos",status_code=status.HTTP_200_OK)
def read_all_todos(user:user_dependency, db:db_dependency):
    if user is None or user.role != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    items = db.query(TodoItems).all()
    return items

@router.delete("/todos/{item_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo( user:user_dependency, db:db_dependency,item_id:int=Path(gt=0)):
    if user is None or user.role != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    item = db.query(TodoItems).filter(TodoItems.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()