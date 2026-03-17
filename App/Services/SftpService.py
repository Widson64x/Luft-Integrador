import os
import paramiko
import datetime as dt

class SftpService:
    
    @staticmethod
    def conectarSftp(host, usuario, senha, porta=22, timeout=15):
        """Estabelece conexão com o servidor SFTP e retorna a sessão."""
        try:
            print(f"Conectando SFTP: {usuario}@{host}:{porta}")
            transport = paramiko.Transport((host, int(porta)))
            transport.banner_timeout = timeout
            transport.auth_timeout = timeout
            transport.connect_timeout = timeout
            
            transport.connect(username=usuario, password=senha)
            sftp = paramiko.SFTPClient.from_transport(transport)
            return sftp
            
        except Exception as erro:
            print(f"Erro ao conectar SFTP {usuario}@{host}:{porta} → {erro}")
            return None

    @staticmethod
    def listarArquivosSeguro(parametros, filtro: str, limite=200):
        """Lista os arquivos no diretório de entrada do SFTP."""
        host = parametros["HOST"]
        usuario = parametros["USER"]
        senha = parametros["PWD"]
        porta = int(parametros.get("PORTA", 22))
        
        entradaBruta = parametros["Entrada"]
        caminhos = [p.strip() for p in entradaBruta.split(';') if p.strip()]
        arquivos = []
        
        sftp = SftpService.conectarSftp(host, usuario, senha, porta)
        if not sftp:
            return arquivos

        try:
            for caminhoAtual in caminhos:
                print(f"Listando Arquivos via SFTP em: {caminhoAtual}")
                try:
                    itens = sftp.listdir_attr(caminhoAtual)
                    
                    for item in itens:
                        if filtro.lower() in item.filename.lower():
                            arquivos.append({
                                "nome": item.filename,
                                "tamanho": f"{item.st_size/1024:.1f} KB",
                                "data": dt.datetime.fromtimestamp(item.st_mtime).strftime("%d/%m/%Y %H:%M"),
                                "timestamp": item.st_mtime,
                                "diretorio_origem": caminhoAtual 
                            })
                        
                        if len(arquivos) >= limite:
                            break
                    if len(arquivos) >= limite:
                        break

                except FileNotFoundError:
                    print(f"⚠️ Aviso: O diretório '{caminhoAtual}' não foi encontrado no servidor.")
                except Exception as erroCaminho:
                    print(f"❌ Erro ao ler diretório '{caminhoAtual}': {erroCaminho}")
                    continue 

            # Ordena por data (mais recente primeiro)
            arquivos.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
            for arq in arquivos:
                arq.pop("timestamp", None)

            return arquivos

        except Exception as erroGeral:
            print(f"Erro crítico ao listar arquivos via SFTP: {erroGeral}")
            return []
        finally:
            sftp.close()

    @staticmethod
    def transferirArquivosSftp(parametros, arquivosCombinados):
        """Realiza o processo de GET e PUT remotamente via SFTP."""
        sftp = SftpService.conectarSftp(
            parametros["HOST"],
            parametros["USER"],
            parametros["PWD"],
            parametros.get("PORTA", 22)
        )    
        
        if not sftp:
            return [{"arquivo": "N/A", "status": "Erro: Falha ao conectar ao SFTP"}]
        
        resultados = []
        os.makedirs("Temp", exist_ok=True) # Usando PascalCase para a pasta também

        try:        
            for index, item in enumerate(arquivosCombinados):
                print(f"\n--- Processando item {index+1}/{len(arquivosCombinados)}: '{item}' ---")
                
                # Separação (Diretório Origem | Nome Arquivo)
                if "|" in item:
                    dirOrigem, nomeArquivo = item.split("|", 1)
                else:
                    dirOrigem = parametros['Entrada'].split(';')[0].strip()
                    nomeArquivo = item

                caminhoRemotoOrigem = f"{dirOrigem.rstrip('/')}/{nomeArquivo}"
                caminhoLocalTemp = f"./Temp/{nomeArquivo}"
                caminhoRemotoDestino = f"{parametros['Saida'].rstrip('/')}/{nomeArquivo}"
                
                try:
                    # 1. Baixar arquivo temporariamente (GET)
                    sftp.get(caminhoRemotoOrigem, caminhoLocalTemp)
                    
                    if not os.path.exists(caminhoLocalTemp):
                        raise Exception("Arquivo não apareceu na pasta Temp após o download.")

                    # 2. Enviar arquivo para o destino final (PUT)
                    sftp.put(caminhoLocalTemp, caminhoRemotoDestino)
                    
                    resultados.append({"arquivo": nomeArquivo, "status": "Sucesso"})
                    
                    # Limpeza do temporário
                    try:
                        os.remove(caminhoLocalTemp)
                    except:
                        pass

                except Exception as erroTransferencia:
                    erroMsg = str(erroTransferencia)
                    print(f"❌ ERRO no processo: {erroMsg}")
                    resultados.append({"arquivo": nomeArquivo, "status": f"Erro: {erroMsg}"})

        finally:
            if sftp:
                sftp.close()
        
        return resultados