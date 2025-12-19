
from fastapi import FastAPI,Request,status
from models import Base
from database import engine 
from routers import auth,todos,admin,user
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
app = FastAPI()

Base.metadata.create_all(bind=engine)



app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def test():
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)

@app.get("/")
def read_root():
  return {"message":"Welcome to the Todo Application API"}

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(user.router)