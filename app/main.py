import uvicorn
from typing import Optional, List
from enum import Enum

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select


class Categories(str, Enum):
    trims = "стрижка"
    coloring = "окрашивание"
    treatment = "лечение"
    styling = "укладка"
    shaving = "бритье"


class Service(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str = Field(index=True)
    categories: Categories = Field(index=True)
    price: float = Field(index=True)
    duration_minutes: int = Field(index=True)
    difficulty_level: int = Field(index=True)
    popularity_score: float = Field(index=True)


class ServiceUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    categories: Optional[Categories] = None
    price: Optional[float] = None
    duration_minutes: Optional[int] = None
    difficulty_level: Optional[int] = None
    popularity_score: Optional[float] = None


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


@app.get("/services/")
def read_services(
        session: Session = Depends(get_session),
        offset: int = 0,
        limit: int = 100,
) -> List[Service]:
    services = session.exec(select(Service).offset(offset).limit(limit)).all()
    return services


@app.get("/services/{service_id}")
def read_service(service_id: int, session: Session = Depends(get_session)) -> Service:
    service = session.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@app.delete("/services/{service_id}")
def delete_service(service_id: int, session: Session = Depends(get_session)):
    service = session.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    session.delete(service)
    session.commit()
    return {"ok": True}


@app.patch("/services/{service_id}", response_model=Service)
def update_service(service_id: int, service_update: ServiceUpdate, session: Session = Depends(get_session)):
    # Получаем объект из базы данных по ID, используя модель Service
    service_db = session.get(Service, service_id)
    if not service_db:
        raise HTTPException(status_code=404, detail="Service not found")

    # Обновляем только переданные поля
    update_data = service_update.dict(exclude_unset=True)  # Получаем данные из ServiceUpdate
    for field, value in update_data.items():
        if value is not None:  # Обновляем только если значение не None
            setattr(service_db, field, value)

    session.add(service_db)
    session.commit()
    session.refresh(service_db)
    return service_db  # Возвращаем обновленный Service


# Заглушка главной страницы
@app.get("/")
def home_page():
    return {"message": "Услуги парикмахерской"}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)