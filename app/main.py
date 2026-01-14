import uvicorn
from typing import Optional, List
from enum import Enum

from fastapi import Depends, FastAPI
from sqlalchemy import true
from sqlmodel import Field, Session, SQLModel, create_engine

class Categories(str, Enum):
    trims = "стрижка"
    coloring = "окрашивание"
    treatment = "лечение"
    styling = "укладка"
    manicure = "маникюр"

class Service(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str = Field(index=True)
    categories: Categories = Field(index=True)
    price: float = Field(index=True)
    duration_minutes: int = Field(index=True)
    difficulty_level: int = Field(index=True)
    popularity_score: float = Field(index=True)

# Соединение с базой данных
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

# Создание базы данных
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Создание зависимости session
def get_session():
    with Session(engine) as session:
        yield session

# Создание базы данных при запуске приложения
app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/services/")
def create_service(service: Service, session: Session = Depends(get_session)) -> Service:
    session.add(service)
    session.commit()
    session.refresh(service)
    return service

# Заглушка главной страницы
@app.get("/")
def home_page():
    return {"message": "Услуги парикмахерской"}

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)