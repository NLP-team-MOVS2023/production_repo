import os
import psycopg2
import pandas as pd
import time

from fastapi import FastAPI, HTTPException
from datetime import datetime

from dotenv import load_dotenv
# from .db.config_reader import config
from .schemas import ObjectSubject
from .ML.pipeline import predict_pipeline

load_dotenv(verbose=True)

# try:
#     HOST_DB = config.HOST_DB.get_secret_value()
#     PORT_DB = config.PORT_DB.get_secret_value()
#     USER_DB = config.USER_DB.get_secret_value()
#     PASSWORD_DB = config.PASSWORD_DB.get_secret_value()
#     NAME_DB = config.NAME_DB.get_secret_value()
# except:
HOST_DB = os.getenv('HOST_DB')
PORT_DB = os.getenv('PORT_DB')
USER_DB = os.getenv('USER_DB')
PASSWORD_DB = os.getenv('PASSWORD_DB')
NAME_DB = os.getenv('NAME_DB')

app = FastAPI()


@app.get('/')
def root() -> str:
    return "Добро пожаловать на сервис для проекта"


@app.get('/ping')
def ping_get():
    return {"message": "OK"}


@app.post('/predict', summary='Predict')
def predict(vals: ObjectSubject, user: str) -> int:
    """Uploads samples and returns predictions as Json"""
    try:
        conn = psycopg2.connect(dbname=NAME_DB, user=USER_DB, password=PASSWORD_DB, host=HOST_DB, port=PORT_DB)
        conn.autocommit = True
        cur = conn.cursor()
    except psycopg2.OperationalError:
        raise HTTPException(status_code=422)

    dict_vals = dict(vals)

    cur.execute('''select max(id) from ml_model_actions;''')
    row = cur.fetchone()
    # if row:
    #     max_id = row[0] + 1
    # else:
    #     max_id = 0

    cur.execute(f"""select id from users where name = '{user}';""")
    row = cur.fetchone()
    try:
        user_id = row[0]
    except TypeError:
        return {"message": "Создайте пользователя /create_user"}

    predicate = predict_pipeline(dict_vals)
    for i in predicate:
        # print(row, max_id)
        cur.execute(f"""
            INSERT
            INTO
            ml_model_actions
            (user_id, timestamp, subject,
            object, predicate, probability)
            VALUES(
                {user_id},\
                {time.mktime(datetime.now().timetuple())},\
                '{predicate[i]['subjects']}',\
                '{predicate[i]['objects']}', \
                '{predicate[i]['predicates']}', \
                {predicate[i]['probabilities']});
            """)

    cur.close()
    conn.close()
    print('Ok')
    return predicate


@app.get('/get_result', summary='Result')
def get_result(res_id: int):
    try:
        conn = psycopg2.connect(dbname=NAME_DB, user=USER_DB, password=PASSWORD_DB, host=HOST_DB, port=PORT_DB)
        conn.autocommit = True
        cur = conn.cursor()
    except psycopg2.OperationalError:
        raise HTTPException(status_code=422)

    cur.execute(f'''select * from ml_model_actions where id = {res_id};''')
    rows = cur.fetchall()
    res = {}
    for i in enumerate(rows):
        res[i] = {'subject': rows[1], 'object': rows[2], 'predicate': rows[3], 'probability': rows[4]}

    cur.close()
    conn.close()
    return res


@app.post('/create_user/{user}')
def create_user(user: str):
    print(user)
    try:
        conn = psycopg2.connect(dbname=NAME_DB, user=USER_DB, password=PASSWORD_DB, host=HOST_DB, port=PORT_DB)
        conn.autocommit = True
        cur = conn.cursor()
    except psycopg2.OperationalError:
        raise HTTPException(status_code=422)

    try:
        base_df = pd.read_sql('select * from users', con=conn)
        # if base_df.empty:
        #     max_id = 0
        # else:
        #     max_id = base_df.id.max() + 1
        if base_df[base_df['name'] == user].empty:
            cur.execute(f'''INSERT
                            INTO
                            users (name, registry_timestamp)
                            VALUES('{user}', {time.mktime(datetime.now().timetuple())});''')
            return {"message": "Юзер удачно добавлен"}
        else:
            return {"message": "Юзер существует"}

        # cur.close()
        # conn.close()
    except KeyError:
        raise HTTPException(status_code=422)


@app.get('/get_all_users')
def get_all_users():
    try:
        conn = psycopg2.connect(dbname=NAME_DB, user=USER_DB, password=PASSWORD_DB, host=HOST_DB, port=PORT_DB)
        conn.autocommit = True

        base_df = pd.read_sql('select * from users', con=conn)
        return base_df.to_dict('records')
    except psycopg2.OperationalError:
        raise HTTPException(status_code=422)


@app.get('/get_all_results')
def get_all_results():
    try:
        conn = psycopg2.connect(dbname=NAME_DB, user=USER_DB, password=PASSWORD_DB, host=HOST_DB, port=PORT_DB)
        conn.autocommit = True

        base_df = pd.read_sql('select * from ml_model_actions', con=conn)
        return base_df.to_dict('records')
    except psycopg2.OperationalError:
        raise HTTPException(status_code=422)
