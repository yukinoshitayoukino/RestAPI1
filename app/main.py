import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
import uvicorn

# Модель данных для услуг
class Service(BaseModel):
    id: int
    name: str
    category: str
    description: str
    price: float
    duration_minutes: int
    difficulty_level: int
    popularity_score: float

