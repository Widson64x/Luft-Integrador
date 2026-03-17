import os
import re
import shutil
import datetime as dt

class TransferenciaService:
    
    @staticmethod
    def transferirArquivosLocal(parametrosInfo, arquivosUpload):
        """
        Move arquivos locais enviados via upload para o destino especificado nas configurações.
        """
        try:
            destino = parametrosInfo.get("Saida")
            if not destino:
                return False, "Destino não informado nos parâmetros."

            # Cria pasta de destino (se não existir)
            os.makedirs(destino, exist_ok=True)

            # Diretório temporário dentro do destino
            pastaTemp = os.path.join(destino, "Temp")
            os.makedirs(pastaTemp, exist_ok=True)

            # Controle de dias válidos (para limpar arquivos muito antigos do Temp)
            hoje = dt.date.today()
            diasValidos = {hoje.strftime("%Y%m%d"), (hoje - dt.timedelta(days=1)).strftime("%Y%m%d")}

            print("=== INÍCIO TRANSFERÊNCIA LOCAL ===")
            print(f"Destino final: {os.path.abspath(destino)}")
            print(f"Arquivos recebidos: {[arq.filename for arq in arquivosUpload]}")

            # Limpeza
            for arquivoAntigo in os.listdir(pastaTemp):
                if not any(dia in arquivoAntigo for dia in diasValidos):
                    os.remove(os.path.join(pastaTemp, arquivoAntigo))

            resultados = []

            for arquivo in arquivosUpload:
                baseNome, extensao = os.path.splitext(arquivo.filename)
                chaveApenasNumeros = re.sub(r"\D", "", baseNome)  # Mantém apenas os números do nome
                novoNomeArquivo = f"{chaveApenasNumeros}{extensao}"

                caminhoTemp = os.path.join(pastaTemp, novoNomeArquivo)
                caminhoDestinoFinal = os.path.join(destino, novoNomeArquivo)

                try:
                    # Salva no Temp e depois move
                    arquivo.save(caminhoTemp)
                    shutil.move(caminhoTemp, caminhoDestinoFinal)
                    
                    print(f"Arquivo transferido: {caminhoDestinoFinal}")
                    resultados.append({"arquivo": novoNomeArquivo, "status": "Sucesso"})
                    
                except Exception as erroArquivo:
                    print(f"Falha ao transferir {arquivo.filename}: {erroArquivo}")
                    resultados.append({"arquivo": arquivo.filename, "status": f"Erro: {erroArquivo}"})

            return True, f"{len(resultados)} arquivo(s) processado(s). Detalhes: {resultados}"

        except Exception as erroGeral:
            print("ERRO GERAL:", erroGeral)
            return False, f"Erro na transferência local: {str(erroGeral)}"