# App/Services/PermissaoService.py
import os
import unicodedata
import json
from functools import wraps
from flask import request, jsonify
from flask_login import current_user
from luftcore.extensions.flask_extension import api_error, render_no_permission, render_403
from App.Db.Connections import GetSqlServerSession 

# Importe suas models correspondentes aqui
from App.Models.SqlServer.Permissoes import Tb_Permissao, Tb_PermissaoGrupo, Tb_PermissaoUsuario, Tb_LogAcesso
from App.Models.SqlServer.Usuario import Usuario

SISTEMA_ID = int(os.getenv("SISTEMA_ID", 3))
DEBUG_PERMISSIONS = os.getenv("DEBUG_PERMISSIONS", "False").lower() == "true"

class PermissaoService:
    @staticmethod
    def _Normalizar(texto):
        if not texto: return ""
        return "".join(c for c in unicodedata.normalize('NFD', texto.upper().strip()) if unicodedata.category(c) != 'Mn')

    @staticmethod
    def VerificarPermissao(UsuarioLogado, ChavePermissao):
        if DEBUG_PERMISSIONS:
            return True

        if not UsuarioLogado.is_authenticated: return False

        Sessao = GetSqlServerSession()
        try:
            id_usuario_logado = UsuarioLogado.get_id()
            
            # Busca o usuário no banco pelo ID
            user_db = Sessao.query(Usuario).filter_by(Codigo_Usuario=id_usuario_logado).first()
            if not user_db: return False

            id_grupo = user_db.codigo_usuariogrupo
            chave_procurada = PermissaoService._Normalizar(ChavePermissao)

            todas_perms = Sessao.query(Tb_Permissao).filter_by(Id_Sistema=SISTEMA_ID).all()
            permissao_encontrada = next((p for p in todas_perms if PermissaoService._Normalizar(p.Chave_Permissao) == chave_procurada), None)
            
            if not permissao_encontrada: return False

            tem_acesso = False
            if id_grupo:
                tem_acesso = Sessao.query(Tb_PermissaoGrupo).filter_by(
                    Id_Permissao=permissao_encontrada.Id_Permissao,
                    Codigo_UsuarioGrupo=id_grupo
                ).count() > 0

            override = Sessao.query(Tb_PermissaoUsuario).filter_by(
                Id_Permissao=permissao_encontrada.Id_Permissao,
                Codigo_Usuario=id_usuario_logado
            ).first()

            return override.Conceder if override else tem_acesso
        except Exception as e:
            print(f"[ERRO] {str(e)}")
            return False
        finally:
            Sessao.close()

    @staticmethod
    def RegistrarLogAcesso(UsuarioLogado, Rota, Metodo, Ip, Chave, Permitido, Parametros=None, Retorno=None):
        Sessao = GetSqlServerSession()
        try:
            # Prioriza o login usado na autenticacao; nome completo entra apenas como fallback.
            nome = (
                getattr(UsuarioLogado, 'nome', None)
                or getattr(UsuarioLogado, 'Login', None)
                or getattr(UsuarioLogado, 'Login_Usuario', None)
                or getattr(UsuarioLogado, 'Nome_Usuario', None)
                or getattr(UsuarioLogado, 'nome_completo', None)
                or 'Anonimo'
            )
            
            NovoLog = Tb_LogAcesso(
                Id_Sistema=SISTEMA_ID,
                Id_Usuario=UsuarioLogado.get_id() if UsuarioLogado.is_authenticated else None,
                Nome_Usuario=nome,
                Rota_Acessada=Rota,
                Metodo_Http=Metodo, 
                Ip_Origem=Ip,
                Permissao_Exigida=Chave.upper(),
                Acesso_Permitido=Permitido,
                Parametros_Requisicao=Parametros,
                Resposta_Acao=Retorno
            )
            Sessao.add(NovoLog)
            Sessao.commit()
        except Exception as e: 
            print(f"[ERRO NO LOG] {str(e)}")
        finally: 
            Sessao.close()

def RequerPermissao(Chave):
    def Decorator(F):
        @wraps(F)
        def Wrapper(*args, **kwargs):
            if DEBUG_PERMISSIONS:
                return F(*args, **kwargs)

            def _is_api(): return request.path.startswith('/api/') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # 1. Se não estiver logado
            if current_user is None or not current_user.is_authenticated:
                return api_error("Faça login", 401) if _is_api() else render_403("Faça login")

            Permitido = PermissaoService.VerificarPermissao(current_user, Chave)

            x_forwarded_for = request.headers.get('X-Forwarded-For')
            ip_real = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.headers.get('X-Real-IP', request.remote_addr)

            params_dict = {}
            if request.args: params_dict['query'] = dict(request.args)
            if request.form: params_dict['form'] = dict(request.form)
            if request.is_json: params_dict['json'] = request.get_json(silent=True)
            parametros_str = json.dumps(params_dict, ensure_ascii=False) if params_dict else None

            # 2. Se NÃO tiver permissão (Aqui entra a tela do LuftCore!)
            if not Permitido:
                msg = f"Acesso negado. Requer: {Chave.upper()}"
                PermissaoService.RegistrarLogAcesso(current_user, request.path, request.method, ip_real, Chave, Permitido, parametros_str, f"Erro 403: {msg}")
                
                return api_error(msg, 403) if _is_api() else render_no_permission(msg)
            
            # 3. Se tiver permissão
            resposta = F(*args, **kwargs)
            retorno_str = f"Status HTTP: {resposta.status_code}" if hasattr(resposta, 'status_code') else "Status HTTP: 200 (OK)"
                
            PermissaoService.RegistrarLogAcesso(current_user, request.path, request.method, ip_real, Chave, Permitido, parametros_str, retorno_str)

            return resposta
        return Wrapper
    return Decorator