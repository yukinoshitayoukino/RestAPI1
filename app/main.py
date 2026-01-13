
from symbol import return_stmt
import uvicorn
from fastapi import FastAPI
from utils import json_to_dict_list
import os
from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationError
import re
app = FastAPI()

class Categories(str, Enum):
    trims = "стрижка"
    coloring = "окрашивание"
    treatment = "лечение"
    styling = "укладка"
    manicure = "маникюр"
class Services(BaseModel):
    id: int
    name: str = Field(default=...,description="название услуги")
    category: Categories = Field(default=...,description="категория услуг")
    description: str = Field(default=...,description="описание услуги")
    price: float = Field(default=...,description="цена услуги")
    duration_minutes: int = Field(default=...,description="длительность")
    difficulty_level: int = Field(default=..., ge=0, le=10,description="сложность от нуля до десяти")
    popularity_score: float = Field(default=..., ge=0, le=10.0,description="популярность услуги, от нуля до десяти")



# Импорт данных из файла со списком услуг
# Получаем путь к директории текущего скрипта
script_dir = os.path.dirname(os.path.abspath(__file__))

# Переходим на уровень выше
parent_dir = os.path.dirname(script_dir)

# Получаем путь к JSON
path_to_json = os.path.join(parent_dir, 'services.json')

# Запрос на получение всех услуг
@app.get("/services")
def get_all_services(id:Optional[int]=None):
    services =  json_to_dict_list(path_to_json)
    if id is None:
        return services
    else:
        return_list = []
        for service in services:
            if service["id"] == id:
                return_list.append(service)
        return return_list

# Заглушка главной страницы
@app.get("/")
def home_page():
    return {"message": "Услуги парикмахерской"}

'''
Основная часть выполнения лабораторной работы
'''
@app.get("/service/",response_model=Services)
def get_service_from_param_id(service_id: int):
    services = json_to_dict_list(path_to_json)
    for service in services:
        if service["id"] == service_id:
            return service

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
