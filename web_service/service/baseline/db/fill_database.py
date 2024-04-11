from config_reader import config
from create_tables_sql import commands

from sqlalchemy import create_engine, text


engine = create_engine(config.connection_url)
conn = engine.connect()

for command in commands:
    conn.execute(text(command))
    conn.commit()

conn.close()
