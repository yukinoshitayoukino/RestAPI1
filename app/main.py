import uvicorn
from typing import Optional, List, Dict, Any
from enum import Enum

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select, func


# Категории оказываемых услуг
class Categories(str, Enum):
    trims = "стрижка"
    coloring = "окрашивание"
    treatment = "лечение"
    styling = "укладка"
    shaving = "бритье"


# Базовый класс для создания услуги
class Service(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )  # Упрощено - autoincrement работает по умолчанию для primary_key
    name: str = Field(index=True)
    description: str = Field(index=True)
    categories: Categories = Field(index=True)
    price: float = Field(index=True)
    duration_minutes: int = Field(index=True)
    difficulty_level: int = Field(index=True)
    popularity_score: float = Field(index=True)


# Модель для создания новой услуги (без id)
class ServiceCreate(SQLModel):
    name: str
    description: str
    categories: Categories  # Валидация Enum
    price: float
    duration_minutes: int
    difficulty_level: int
    popularity_score: float


# Модель для обновления услуги (для реализации возможности частичного обновления тип поля Optional)
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


""" Эта часть отвечает за список запросов и сортировку """


# Создание новой услуги.
@app.post("/services/")
def create_service(service: ServiceCreate, session: Session = Depends(get_session)) -> Service:
    # Преобразуем ServiceCreate в Service
    service_data = service.dict()
    db_service = Service(
        name=service_data["name"],
        description=service_data["description"],
        categories=service_data["categories"],
        price=service_data["price"],
        duration_minutes=service_data["duration_minutes"],
        difficulty_level=service_data["difficulty_level"],
        popularity_score=service_data["popularity_score"]
    )
    session.add(db_service)
    session.commit()
    session.refresh(db_service)
    return db_service


# Получение услуги с возможностью сортировки
@app.get("/services/")
def read_services(
        session: Session = Depends(get_session),
        offset: int = 0,
        limit: int = 100,
        sort_by: str = Query("id",
                             description="Поле для сортировки (id, name, price, duration_minutes, difficulty_level, popularity_score)"),
        sort_order: str = Query("asc", description="Порядок сортировки (asc или desc)")
) -> List[Service]:
    # Определяем поле для сортировки
    sort_field_map = {
        "id": Service.id,
        "name": Service.name,
        "price": Service.price,
        "duration_minutes": Service.duration_minutes,
        "difficulty_level": Service.difficulty_level,
        "popularity_score": Service.popularity_score
    }

    sort_field = sort_field_map.get(sort_by, Service.id)

    # Определяем порядок сортировки
    if sort_order.lower() == "desc":
        sort_field = sort_field.desc()
    else:
        sort_field = sort_field.asc()

    # Выполняем запрос с сортировкой
    query = select(Service).order_by(sort_field).offset(offset).limit(limit)
    services = session.exec(query).all()
    return services


# Получение статистики по числовым полям
@app.get("/services/statistics")
def get_service_statistics(
        session: Session = Depends(get_session)
) -> Dict[str, Dict[str, Any]]:
    # Вычисляем статистику для каждого числового поля
    price_stats = session.exec(
        select(
            func.avg(Service.price).label("avg"),
            func.min(Service.price).label("min"),
            func.max(Service.price).label("max"),
            func.count(Service.price).label("count")
        )
    ).first()

    duration_stats = session.exec(
        select(
            func.avg(Service.duration_minutes).label("avg"),
            func.min(Service.duration_minutes).label("min"),
            func.max(Service.duration_minutes).label("max"),
            func.count(Service.duration_minutes).label("count")
        )
    ).first()

    difficulty_stats = session.exec(
        select(
            func.avg(Service.difficulty_level).label("avg"),
            func.min(Service.difficulty_level).label("min"),
            func.max(Service.difficulty_level).label("max"),
            func.count(Service.difficulty_level).label("count")
        )
    ).first()

    popularity_stats = session.exec(
        select(
            func.avg(Service.popularity_score).label("avg"),
            func.min(Service.popularity_score).label("min"),
            func.max(Service.popularity_score).label("max"),
            func.count(Service.popularity_score).label("count")
        )
    ).first()

    # Преобразуем результаты в словарь
    return {
        "price": {
            "average": float(price_stats[0]) if price_stats[0] is not None else 0,
            "minimum": float(price_stats[1]) if price_stats[1] is not None else 0,
            "maximum": float(price_stats[2]) if price_stats[2] is not None else 0,
            "count": price_stats[3] if price_stats[3] is not None else 0
        },
        "duration_minutes": {
            "average": float(duration_stats[0]) if duration_stats[0] is not None else 0,
            "minimum": duration_stats[1] if duration_stats[1] is not None else 0,
            "maximum": duration_stats[2] if duration_stats[2] is not None else 0,
            "count": duration_stats[3] if duration_stats[3] is not None else 0
        },
        "difficulty_level": {
            "average": float(difficulty_stats[0]) if difficulty_stats[0] is not None else 0,
            "minimum": difficulty_stats[1] if difficulty_stats[1] is not None else 0,
            "maximum": difficulty_stats[2] if difficulty_stats[2] is not None else 0,
            "count": difficulty_stats[3] if difficulty_stats[3] is not None else 0
        },
        "popularity_score": {
            "average": float(popularity_stats[0]) if popularity_stats[0] is not None else 0,
            "minimum": float(popularity_stats[1]) if popularity_stats[1] is not None else 0,
            "maximum": float(popularity_stats[2]) if popularity_stats[2] is not None else 0,
            "count": popularity_stats[3] if popularity_stats[3] is not None else 0
        }
    }


# Получение услуги по ID
@app.get("/services/{service_id}")
def read_service(service_id: int, session: Session = Depends(get_session)) -> Service:
    service = session.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


# Удаление услуги
@app.delete("/services/{service_id}")
def delete_service(service_id: int, session: Session = Depends(get_session)):
    service = session.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    session.delete(service)
    session.commit()
    return {"ok": True}


# Обновление существующей услуги
@app.patch("/services/{service_id}", response_model=Service)
def update_service(service_id: int, service_update: ServiceUpdate, session: Session = Depends(get_session)):
    service_db = session.get(Service, service_id)
    if not service_db:
        raise HTTPException(status_code=404, detail="Service not found")

    update_data = service_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(service_db, field, value)

    session.add(service_db)
    session.commit()
    session.refresh(service_db)
    return service_db


# Заглушка главной страницы
@app.get("/")
def home_page():
    return {"message": "Услуги парикмахерской"}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)