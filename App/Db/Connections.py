# App/Db/Connections.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

def get_sqlserver_uri():
    """Constrói a URI de conexão para o SQL Server usando variáveis de ambiente.
    e retorna a URI formatada para uso com SQLAlchemy e o driver pyodbc.
    Returns:
        str: URI de conexão para o SQL Server.
    """
    user = os.getenv("SQLDB_USER")
    password = os.getenv("SQLDB_PASS")
    host = os.getenv("SQLDB_HOST")
    port = os.getenv("SQLDB_PORT", "1433")
    db = os.getenv("SQLDB_NAME")
    
    # Para SQL Server via pyodbc, o host e porta costuma ser separados por vírula no DSN
    # Exemplo: 172.16.200.3,1433
    server_address = f"{host},{port}"
    
    return f"mssql+pyodbc://{user}:{password}@{server_address}/{db}?driver=ODBC+Driver+17+for+SQL+Server"
    

def GetSqlServerSession():
    """Obtem uma sessão de banco de dados SQL Server usando SQLAlchemy.
    e configura a conexão para não usar pool de conexões (NullPool) e habilitar o pool_pre_ping para verificar conexões inativas.
    Returns:
        sqlalchemy.orm.session.Session: Sessão de banco de dados SQL Server.
    """
    # O pool_pre_ping é útil para evitar erros de conexão inativa, especialmente em ambientes onde as conexões podem ser 
    # fechadas pelo servidor. E o NullPool é usado para garantir que cada sessão obtenha uma nova conexão, sem reutilizar 
    # conexões anteriores.
    engine = create_engine(get_sqlserver_uri(), pool_pre_ping=True, poolclass=NullPool)
    return sessionmaker(bind=engine)()