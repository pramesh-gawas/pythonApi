
from fastapi import APIRouter,Depends,Path,HTTPException,Request,status
from typing import Annotated
from pydantic import BaseModel,Field
from models import TodoItems
from sqlalchemy.orm import Session
from database import sessionmaker as SessionLocal
from starlette import status  
from routers.auth import get_current_user
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter(
    prefix='/todos', 
    tags=["todos"]
)

def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
user_dependency = Annotated[dict,Depends(get_current_user)]
db_dependency = Annotated[Session,Depends(get_db)]

class TodoItemRequest(BaseModel):
    title: str =Field(min_length=1, max_length=100)
    description: str  = Field(min_length=1, max_length=100)
    completed: bool
    priority: int = Field(gt=0 ,lt=6)
    
def redirect_to_login():
    redirect_response =  RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response


@router.get("/edit-todo-page/{item_id}",response_class=RedirectResponse)
async def edit_todo_page(request:Request, db:db_dependency, item_id:int = Path(gt=0)):
    try:
        user = await get_current_user(request.cookies.get("access_token"),db)
        if user is None:
            return redirect_to_login()
        todo = db.query(TodoItems).filter(TodoItems.id == item_id).filter(TodoItems.owner_id == user.id).first()
        if todo is None:
            return redirect_to_login()
        return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})
    except Exception as e:
        print(e)
        return redirect_to_login()

# pages

@router.get("/todo-page",response_class=RedirectResponse)
async def read_todos_page(request:Request, db:db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"),db)
        if user is None:
            return redirect_to_login()
        todos = db.query(TodoItems).filter(TodoItems.owner_id == user.id).all()
        return templates.TemplateResponse("todo.html", {"request": request, "todos": todos, "user": user})
    except Exception as e:
        print(e)
        return redirect_to_login()

@router.get("/add-todo-page",response_class=RedirectResponse)
async def add_todo_page(request:Request, db:db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"),db)
        if user is None:
            return redirect_to_login()
        return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})
    except Exception as e:
        print(e)
        return redirect_to_login()
# endpoints

@router.get("/",status_code=status.HTTP_200_OK)
def read_all(user:user_dependency, db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    items = db.query(TodoItems).filter(TodoItems.owner_id == user.id).all()
    return items

@router.get("/todo/{item_id}" ,status_code=status.HTTP_200_OK)
async def read_item( user:user_dependency, db:db_dependency,item_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    item = db.query(TodoItems).filter(TodoItems.id == item_id).filter(TodoItems.owner_id == user.id).first()
    if item is not None:
        return item
    raise HTTPException(status_code=404, detail="Item not found")


@router.post("/todo",status_code=status.HTTP_201_CREATED)
async def create_item( user:user_dependency, request:TodoItemRequest, db:Annotated[Session,Depends(get_db)]):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    new_item = TodoItems(
        title=request.title,
        description=request.description,
        completed=request.completed,
        priority=request.priority,
        owner_id=user.id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)


@router.put("/todo/{item_id}",status_code=status.HTTP_200_OK)
async def update_item(user:user_dependency, request:TodoItemRequest, db:Annotated[Session,Depends(get_db)], item_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    item = db.query(TodoItems).filter(TodoItems.id == item_id).filter(TodoItems.owner_id == user.id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item.title = request.title
    item.description = request.description
    item.completed = request.completed
    
    db.commit()
    db.refresh(item)
    return item


@router.delete("/todo/{item_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(user:user_dependency, db:db_dependency, item_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    item = db.query(TodoItems).filter(TodoItems.id == item_id).filter(TodoItems.owner_id == user.id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(item)
    db.commit()
    return None