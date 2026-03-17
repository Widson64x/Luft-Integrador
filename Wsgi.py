import os
from waitress import serve
from app import create_app

BASE_PREFIX = "/EDI_Transfer" # BASE_PREFIX PARA 'http://127.0.0.1:9005/EDI_Transfer'

if __name__ == "__main__":
    print(f"Acesse: http://127.0.0.1:{os.environ.get('PORT', 9005)}{BASE_PREFIX}")
    app = create_app()
    HOST = os.getenv("APP_HOST", "127.0.0.1")
    PORT = int(os.getenv("APP_PORT", "9005"))  # alinhe com o Nginx
    serve(app, host=HOST, port=PORT, threads=100)
