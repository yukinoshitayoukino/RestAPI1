import uvicorn
from fastapi import FastAPI, HTTPException
from utils import json_to_dict_list as utils_json_to_dict
import os
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field

app = FastAPI()

# Получаем абсолютный путь к services.json (на уровень выше)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICES_JSON_PATH = os.path.join(BASE_DIR, '..', 'services.json')
# Нормализуем путь (убираем '..' и т.д.)
SERVICES_JSON_PATH = os.path.normpath(SERVICES_JSON_PATH)

print(f"Путь к services.json: {SERVICES_JSON_PATH}")
print(f"Файл существует: {os.path.exists(SERVICES_JSON_PATH)}")


class Categories(str, Enum):
    trims = "стрижка"
    coloring = "окрашивание"
    treatment = "лечение"
    styling = "укладка"
    manicure = "маникюр"


class Services(BaseModel):
    id: int
    name: str = Field(description="название услуги")
    category: Categories = Field(description="категория услуг")
    description: str = Field(description="описание услуги")
    price: float = Field(description="цена услуги")
    duration_minutes: int = Field(description="длительность")
    difficulty_level: int = Field(ge=0, le=10, description="сложность от нуля до десяти")
    popularity_score: float = Field(ge=0, le=10.0, description="популярность услуги, от нуля до десяти")


# Запрос на получение всех услуг
@app.get("/services")
def get_all_services(id: Optional[int] = None):
    # Используем полный путь
    services = utils_json_to_dict(SERVICES_JSON_PATH)

    if id is None:
        return services
    else:
        for service in services:
            if service["id"] == id:
                return [service]
        return []


# Заглушка главной страницы
@app.get("/")
def home_page():
    return {"message": "Услуги парикмахерской"}


# Получение конкретного сервиса
@app.get("/service/", response_model=Services)
def get_service_from_param_id(service_id: int):
    services = utils_json_to_dict(SERVICES_JSON_PATH)
    for service in services:
        if service["id"] == service_id:
            return Services(**service)
    raise HTTPException(status_code=404, detail="Service not found")


# Инициализация JSONDatabase с правильным путем
try:
    from json_db_lite import JSONDatabase

    # Для JSONDatabase также нужен правильный путь
    small_db = JSONDatabase(file_path=SERVICES_JSON_PATH)


    def get_all_services_from_db():
        return small_db.get_all_records()


    def add_service_to_db(service: dict):
        # Проверка уникальности ID
        existing = small_db.get_all_records()
        for item in existing:
            if item.get('id') == service.get('id'):
                raise ValueError(f"Service with id {service['id']} already exists")

        small_db.add_records(service)
        return True


    @app.post("/add_service")
    def add_service_handler(service: Services):
        try:
            service_dict = service.dict()
            add_service_to_db(service_dict)
            return {"message": "Сервис успешно добавлен!", "id": service.id}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при добавлении сервиса: {str(e)}")

except ImportError:
    print("Модуль json_db_lite не найден. Функции работы с БД будут недоступны.")


    @app.post("/add_service")
    def add_service_handler(service: Services):
        raise HTTPException(status_code=501, detail="Database functionality not available")

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
