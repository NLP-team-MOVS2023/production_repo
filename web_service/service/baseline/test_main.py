from fastapi.testclient import TestClient
from main import app
import pandas as pd

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.text == '"Добро пожаловать на сервис для проекта"'


def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}


def test_create_user():
    response = client.post(
        "/create_user/abcdefg",
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Юзер удачно добавлен"}


def test_create_existing_user():
    response = client.post(
        "/create_user/abcdefg",
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Юзер существует"}


def test_predict():
    vals = pd.DataFrame.from_dict({'objects': ['table'], 'subjects': ['apple']})
    response = client.post("/predict", json={"vals": vals.to_dict(orient="list"), "user": "abcdefg"})
    assert response.status_code == 200


def test_predict_user_nonexistent():
    vals = pd.DataFrame.from_dict({'objects': ['table'], 'subjects': ['apple']})
    response = client.post("/predict", json={"vals": vals.to_dict(orient="list"), "user": "gfedcba"})
    assert response.status_code == 200
    assert response.json() == {"message": "Создайте пользователя /create_user"}


def test_get_result():
    response = client.get("/get_result/0")
    assert response.status_code == 404


def test_get_all_users():
    response = client.get("/get_all_users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_all_results():
    response = client.get("/get_all_results")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
