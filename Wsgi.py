import os
from waitress import serve
from App import criarApp

BASE_PREFIX = os.getenv("BASE_PREFIX", "/Luft-Integrador")

if __name__ == "__main__":
    app = criarApp()
    HOST = os.getenv("APP_HOST", "127.0.0.1")
    PORT = int(os.getenv("APP_PORT", "9005"))
    
    print(f"Acesse: http://{HOST}:{PORT}{BASE_PREFIX}")
    
    # O url_prefix AQUI vai ensinar corretamente o LuftCore a buscar o CSS/JS
    serve(app, host=HOST, port=PORT, threads=100, url_prefix=BASE_PREFIX)