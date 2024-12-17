# In docker container
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg2://USERNAME:PASSWORD@host.docker.internal:5432/postgres")
connection = engine.connect()
print("Connection successful!")
connection.close()
