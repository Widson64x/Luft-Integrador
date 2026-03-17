# App/Db/Connections.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# URL de conexão (Exemplo usando pyodbc para SQL Server)
def get_sqlserver_uri():
    user = os.getenv("SQLDB_USER")
    password = os.getenv("SQLDB_PASS")
    host = os.getenv("SQLDB_HOST")
    port = os.getenv("SQLDB_PORT", "1433")
    db = os.getenv("SQLDB_NAME")
    return f"mssql+pyodbc://{user}:{password}@{host}:{port}/{db}?driver=ODBC+Driver+17+for+SQL+Server"

def GetSqlServerSession():
    engine = create_engine(get_sqlserver_uri(), pool_pre_ping=True)
    return sessionmaker(bind=engine)()