import psycopg2
import pandas as pd
import time

from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends, Body

from sqlalchemy import create_engine, text, Column, Integer, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.mysql import VARCHAR

from service.baseline.db.config_reader import config
from service.baseline.schemas import ObjectSubject, ObjectContext
from service.baseline.ML.pipeline import predict_pipeline
from service.baseline.DL.dl_pipeline import predict_pipeline_dl

engine = create_engine(config.connection_url)
try:
    engine.connect()
except SQLAlchemyError:
    raise HTTPException(status_code=422)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, unique=True, primary_key=True)
    name = Column(VARCHAR(100))
    registry_timestamp = Column(Integer)


class MlModel(Base):
    __tablename__ = "ml_model_actions"

    id = Column(Integer, unique=True, primary_key=True)
    user_id = Column(Integer)
    timestamp = Column(Integer)
    subject = Column(VARCHAR(100))
    object = Column(VARCHAR(100))
    predicate = Column(VARCHAR(100))
    probability = Column(Float)


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


@app.get("/")
def root() -> str:
    return "Добро пожаловать на сервис для проекта"


@app.get("/ping")
def ping_get():
    return {"message": "OK"}


@app.post("/predict", summary="Predict")
def predict(
    vals: ObjectSubject, user: Annotated[int, Body()], db: Session = Depends(get_db)
) -> int | dict:
    """Uploads samples and returns predictions as Json"""

    dict_vals = dict(vals)

    row = db.execute(text("""select max(id) from ml_model_actions;""")).fetchone()

    row = db.execute(
        text(f"""select id from users where name = '{user}';""")
    ).fetchone()
    try:
        user_id = row[0]
    except TypeError:
        return {"message": "Создайте пользователя /create_user"}
    predicate = predict_pipeline(dict_vals)
    for i in predicate:
        db_mlmodel = MlModel(
            user_id=user_id,
            timestamp=time.mktime(datetime.now().timetuple()),
            subject=predicate[i]["subjects"],
            object=predicate[i]["objects"],
            predicate=predicate[i]["predicates"],
            probability=predicate[i]["probabilities"],
        )
        db.add(db_mlmodel)
        db.commit()

    return predicate


@app.post("/predict_dl", summary="Predict")
def predict_dl(
    vals: ObjectContext, user: Annotated[int, Body()], db: Session = Depends(get_db)
) -> int | dict:
    """Uploads samples and returns predictions as Json"""

    dict_vals = dict(vals)
    attributes = predict_pipeline_dl(dict_vals)

    return attributes


@app.get("/get_result", summary="Result")
def get_result(res_id: int, db: Session = Depends(get_db)):

    rows = db.execute(text(f"""select * from ml_model_actions where id = {res_id};""")).fetchall()
    res = {}
    for i in enumerate(rows):
        res[i] = {
            "subject": rows[1],
            "object": rows[2],
            "predicate": rows[3],
            "probability": rows[4],
        }

    return res


@app.post("/create_user/{user}")
def create_user(user: str, db: Session = Depends(get_db)):
    try:
        base_df = pd.read_sql(text("select * from users"), con=db.connection())

        if base_df[base_df["name"] == user].empty:
            db_user = User(
                name=user, registry_timestamp=time.mktime(datetime.now().timetuple())
            )
            db.add(db_user)
            db.commit()
            return {"message": "Юзер удачно добавлен"}

        else:
            return {"message": "Юзер существует"}
    except KeyError:
        raise HTTPException(status_code=422)


@app.get("/get_all_users")
def get_all_users(db: Session = Depends(get_db)):
    try:
        base_df = pd.read_sql(text("select * from users"), con=db.connection())
        return base_df.to_dict("records")
    except psycopg2.OperationalError:
        raise HTTPException(status_code=422)


@app.get("/get_all_results")
def get_all_results(db: Session = Depends(get_db)):
    try:
        base_df = pd.read_sql(
            text("select * from ml_model_actions"), con=db.connection()
        )
        return base_df.to_dict("records")
    except psycopg2.OperationalError:
        raise HTTPException(status_code=422)
