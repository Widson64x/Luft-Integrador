# App/Db/Connections.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# URL de conexão (Exemplo usando pyodbc para SQL Server)
# App/Db/Connections.py

def get_sqlserver_uri():
    user = os.getenv("SQLDB_USER")
    password = os.getenv("SQLDB_PASS")
    host = os.getenv("SQLDB_HOST")
    port = os.getenv("SQLDB_PORT", "1433")
    db = os.getenv("SQLDB_NAME")
    
    # Para SQL Server via pyodbc, o host e porta costumam ser separados por vírgula no DSN
    # Exemplo: 172.16.200.3,1433
    server_address = f"{host},{port}"
    
    return f"mssql+pyodbc://{user}:{password}@{server_address}/{db}?driver=ODBC+Driver+17+for+SQL+Server"

def GetSqlServerSession():
    engine = create_engine(get_sqlserver_uri(), pool_pre_ping=True, poolclass=NullPool)
    return sessionmaker(bind=engine)()