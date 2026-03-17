import pandas as pd

class ExcelService:
    CAMINHO_PLANILHA = "Data/IntParametros.xlsx"

    @classmethod
    def carregarClientes(cls, usuario: str):
        df = pd.read_excel(cls.CAMINHO_PLANILHA, sheet_name="Reintegracao")    
        cliente = df["Cliente"]
        if cliente.empty:
            return []
        return cliente

    @classmethod
    def carregarParametrosReintegracao(cls, cliente: str):
        try:
            df = pd.read_excel(cls.CAMINHO_PLANILHA, sheet_name="Reintegracao")
            df["Dominio"] = "luftfarma"
            
            linha = df[df["Cliente"] == cliente]
            if linha.empty:
                return None
            
            return linha.iloc[0].to_dict()
        except Exception as erro:
            print(f"Erro ao carregar parâmetros para {cliente}: {erro}")
            return None