import os
from dotenv import load_dotenv

# 1º - CARREGA AS VARIÁVEIS DE AMBIENTE PRIMEIRO!
load_dotenv()

# 2º - SÓ DEPOIS IMPORTA A APLICAÇÃO E O SERVIDOR
from waitress import serve
from App import criarApp

BASE_PREFIX = os.getenv("BASE_PREFIX", "/Luft-Integrador")

if __name__ == "__main__":
    app = criarApp()
    HOST = os.getenv("APP_HOST", "127.0.0.1")
    PORT = int(os.getenv("APP_PORT", "9005"))
    
    print(f"Acesse: http://{HOST}:{PORT}{BASE_PREFIX}")
    
    serve(app, host=HOST, port=PORT, threads=6, url_prefix=BASE_PREFIX)