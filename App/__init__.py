import os
from flask import Flask
from flask_login import LoginManager, current_user
from werkzeug.middleware.proxy_fix import ProxyFix

# Importações do seu framework LuftCore (Ajuste conforme o path real do seu framework)
from luftcore.extensions.flask_extension import LuftCorePackages, LuftUser


from App.Models.UsuarioModel import UsuarioModel

BASE_PREFIX = "/Luft-Integrador"

def criarApp():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "Templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "Static"),
        static_url_path=f"{BASE_PREFIX}/Static",
    )

    app.secret_key = os.getenv("APP_SECRET_KEY", "supersegredo")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    app.config["APPLICATION_ROOT"] = BASE_PREFIX

    # Configuração do Flask-Login
    gerenciadorLogin = LoginManager()
    gerenciadorLogin.init_app(app)
    gerenciadorLogin.login_view = 'main.index'

    @gerenciadorLogin.user_loader
    def carregarUsuario(usuarioId):
        return UsuarioModel.obterPorId(usuarioId)

    # Injeção do Framework LuftCore
    gerenciadorUsuario = LuftUser(
        callback_usuario=lambda: current_user,
        attr_nome='nome',          # Atributo obrigatório
        email='email',             # Atributos extras mapeados para o front
        cargo='nome_grupo',        # Usando grupo de permissão como 'cargo'
        nome_completo='nome_completo'
    )

    luftcoreApp = LuftCorePackages(
        app=app,
        app_name="Luft-Integrador",
        gerenciador_usuario=gerenciadorUsuario,
        inject_theme=True,         
        inject_global=True,        
        inject_animations=True,    
        inject_js=True,             
        show_topbar=True,         
        show_search=False,        
        show_notifications=False, 
        show_breadcrumb=True      
    )

    # Registro das Rotas
    from App.Routes.Main import bp
    app.register_blueprint(bp, url_prefix=BASE_PREFIX)
    from App.Routes.Seguranca import security_bp
    app.register_blueprint(security_bp, url_prefix=BASE_PREFIX)

    return app