import psycopg2
import os
from sqlalchemy import create_engine
from create_tables_sql import commands

HOST_DB = 'dpg-cnvk5fn79t8c73d73pm0-a.frankfurt-postgres.render.com'
PORT_DB = 5432
USER_DB = 'nlp_project'
PASSWORD_DB = '04H5GFKU1hGSMaJrljaN7IYQZViry9oW'
NAME_DB = 'nlp_project_sgxl'

print(os.listdir())
print(HOST_DB, PORT_DB, USER_DB, PASSWORD_DB, NAME_DB)
conn = psycopg2.connect(dbname=NAME_DB, user=USER_DB, password=PASSWORD_DB, host=HOST_DB,
                        port=PORT_DB, sslmode='require')
conn.autocommit = True
engine = create_engine(f'postgres://nlp_project:04H5GFKU1hGSMaJrljaN7IYQZViry9oW@dpg-cnvk5fn79t8c73d73pm0-a.frankfurt-postgres.render.com')
with conn.cursor() as cur:
    for command in commands:
        cur.execute(command)

cur.close()
conn.close()
