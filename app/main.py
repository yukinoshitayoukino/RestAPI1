from fastapi import FastAPI
from utils import json_to_dict_list
import os
from typing import Optional
app = FastAPI()



# Импорт данных из файла со списокм услуг
# Получаем путь к директории текущего скрипта
script_dir = os.path.dirname(os.path.abspath(__file__))

# Переходим на уровень выше
parent_dir = os.path.dirname(script_dir)

# Получаем путь к JSON
path_to_json = os.path.join(parent_dir, 'services.json')

# Запрос на получение всех услуг
@app.get("/services")
def get_all_services():
    return json_to_dict_list("services.json")
# Заглушка главной страницы
@app.get("/")
def home_page():
    return {"message": "Услуги парикмахерской"}

'''
Основная часть выполнения лабораторной работы
'''