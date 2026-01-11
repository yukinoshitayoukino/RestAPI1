from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()


class User(BaseModel):
    name: str
    age: int


@app.get('/users/{user_id}')
def get_user(user_id):
    return User(name="John Doe", age=20)

@app.put('/users/{user_id}')
def update_user(user_id, user: User):
# поместите сюда код для обновления данных
    return user

