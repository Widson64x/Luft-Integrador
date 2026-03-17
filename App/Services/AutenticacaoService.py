import paramiko
from ldap3 import Server, Connection, NTLM, core
from App.Db.Connections import GetSqlServerSession
from App.Models.SqlServer.Usuario import Usuario, UsuarioGrupo

class AutenticacaoService:
    
    @staticmethod
    def autenticarUsuario(servidorLdap, dominio, usuario, senha):
        try:
            # 1. Tenta Autenticar no AD
            server = Server(servidorLdap, port=389, use_ssl=False, get_info=None) 
            Connection(server, user=f'{dominio}\\{usuario}', password=senha, authentication=NTLM, auto_bind=True)
            print(f"Autenticação de {usuario} bem-sucedida no AD!")
            
            # 2. Busca o Usuário no Banco de Dados
            Sessao = GetSqlServerSession()
            try:
                # Procura pelo login digitado
                user_db = Sessao.query(Usuario).filter_by(Login_Usuario=usuario).first()
                
                if not user_db:
                    print("Usuário existe no AD, mas não está cadastrado na base de dados do sistema.")
                    return False, None
                
                # Busca o nome do Grupo
                grupo_db = Sessao.query(UsuarioGrupo).filter_by(codigo_usuariogrupo=user_db.codigo_usuariogrupo).first()
                nome_grupo = grupo_db.Sigla_UsuarioGrupo if grupo_db else "Sem Grupo"

                # Monta o dicionário de dados do usuário
                dados_usuario = {
                    "id_banco": user_db.Codigo_Usuario,
                    "login": user_db.Login_Usuario,
                    "nome_completo": user_db.Nome_Usuario or user_db.Login_Usuario,
                    "email": user_db.Email_Usuario or f"{usuario}@luftlogistics.com",
                    "id_grupo": user_db.codigo_usuariogrupo,
                    "nome_grupo": nome_grupo
                }
                
                return True, dados_usuario
            finally:
                Sessao.close()
                
        except core.exceptions.LDAPBindError as erro:
            print("Falha na autenticação (Usuário ou senha incorretos):", erro)
            return False, None
        except Exception as e:
            print(f"Erro geral durante login: {e}")
            return False, None