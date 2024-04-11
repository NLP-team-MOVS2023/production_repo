import pandas as pd
from fastapi.testclient import TestClient
from service.baseline.main import app, engine, Base, User, Session, get_db


def override_get_db():
    if not engine.url.get_backend_name() == "sqlite":
        raise RuntimeError("Use SQLite backend to run tests")
    Base.metadata.create_all(bind=engine)
    try:
        with Session() as db:
            test_user = User(name=0, registry_timestamp=0)
            db.add(test_user)
            db.commit()
            yield db
    finally:
        Base.metadata.drop_all(bind=engine)


app.dependency_overrides[get_db] = override_get_db


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
        "/create_user/1",
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Юзер удачно добавлен"}


def test_create_existing_user():
    response = client.post(
        "/create_user/0",
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Юзер существует"}


def test_predict():
    vals = pd.DataFrame.from_dict({"objects": ["table"], "subjects": ["apple"]})
    response = client.post(
        "/predict", json={"vals": vals.to_dict(orient="list"), "user": 0}
    )
    assert response.status_code == 200


def test_predict_user_nonexistent():
    vals = pd.DataFrame.from_dict({"objects": ["table"], "subjects": ["apple"]})
    response = client.post(
        "/predict", json={"vals": vals.to_dict(orient="list"), "user": 5}
    )
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
