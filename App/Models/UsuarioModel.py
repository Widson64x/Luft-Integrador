from flask_login import UserMixin
from App.Db.Connections import GetSqlServerSession
from App.Models.SqlServer.Usuario import Usuario, UsuarioGrupo

class UsuarioModel(UserMixin):
    def __init__(self, id_banco, username, nome_completo, email, nome_grupo, permissoes=None):
        self.id = str(id_banco)  # O Flask-Login exige que o ID seja salvo como string
        self.nome = username
        self.email = email
        self.nome_completo = nome_completo.capitalize()
        self.nome_grupo = nome_grupo
        self.permissoes = permissoes or []

    @staticmethod
    def obterPorId(usuarioId):
        """
        Esta função é chamada pelo Flask-Login a cada requisição para recriar o usuário logado.
        Vamos buscar os dados frescos do banco.
        """
        Sessao = GetSqlServerSession()
        try:
            # Busca pelo ID
            user_db = Sessao.query(Usuario).filter_by(Codigo_Usuario=int(usuarioId)).first()
            if user_db:
                grupo_db = Sessao.query(UsuarioGrupo).filter_by(codigo_usuariogrupo=user_db.codigo_usuariogrupo).first()
                nome_grupo = grupo_db.Sigla_UsuarioGrupo if grupo_db else "Sem Grupo"
                
                return UsuarioModel(
                    id_banco=user_db.Codigo_Usuario,
                    username=user_db.Login_Usuario,
                    nome_completo=user_db.Nome_Usuario or user_db.Login_Usuario,
                    email=user_db.Email_Usuario or f"{user_db.Login_Usuario}@luftlogistics.com",
                    nome_grupo=nome_grupo
                )
            return None
        except Exception as e:
            print(f"Erro ao recuperar sessão do usuário: {e}")
            return None
        finally:
            Sessao.close()