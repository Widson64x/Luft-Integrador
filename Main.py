import sys
import io
import os
from App import criarApp

BASE_PREFIX = "/Luft-Integrador"

# Força a saída padrão para UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

app = criarApp()

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 9005))
    print(f"Acesse: http://127.0.0.1:{porta}{BASE_PREFIX}")
    app.run(host="127.0.0.1", port=porta, debug=True)