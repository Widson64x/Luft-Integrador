import pandas as pd
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user

from App.Models.UsuarioModel import UsuarioModel
from App.Services.AutenticacaoService import AutenticacaoService    
from App.Services.ExcelService import ExcelService  
from App.Services.SftpService import SftpService
from App.Services.TransferenciaService import TransferenciaService

# Importação do serviço de permissão
from App.Services.PermissaoService import RequerPermissao, PermissaoService, DEBUG_PERMISSIONS

bp = Blueprint("main", __name__)

@bp.route("/", methods=["GET", "POST"])
#@RequerPermissao('INTEGRADOR.VISUALIZAR')
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        dominio = "luftfarma"
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        sucesso, dados_usuario = AutenticacaoService.autenticarUsuario("luftfarma.com.br", dominio, usuario, senha)
        
        if sucesso and dados_usuario:
            # Removido o carregamento de processos via Excel
            
            usuarioObj = UsuarioModel(
                id_banco=dados_usuario["id_banco"],
                username=dados_usuario["login"],
                nome_completo=dados_usuario["nome_completo"],
                email=dados_usuario["email"],
                nome_grupo=dados_usuario["nome_grupo"]
                # permissoes=processos foi removido
            )
            login_user(usuarioObj)
            
            # Removido o session["processos"] = processos
            return redirect(url_for("main.home"))
        else:
            flash("Utilizador/senha inválidos no AD ou não cadastrado na base de dados do sistema.", "erro")
            return render_template("Login.html")

    return render_template("Login.html")

@bp.route("/home")
@login_required
@RequerPermissao('INTEGRADOR.VISUALIZAR')
def home():
    pode_ecobox = True if DEBUG_PERMISSIONS else PermissaoService.VerificarPermissao(current_user, 'XML_ECOBOX.SINCRONIZAR')
    pode_reintegracao = True if DEBUG_PERMISSIONS else PermissaoService.VerificarPermissao(current_user, 'REINTEGRACAO_WMS.VISUALIZAR')
    return render_template(
        "Home.html",
        usuario=current_user.nome,
        pode_ecobox=pode_ecobox,
        pode_reintegracao=pode_reintegracao,
        # Removido o processos=session.get("processos", [])
    )

# --- ROTAS DO MÓDULO XML_ECOBOX ---

@bp.route("/upload-local", methods=["POST"])
@login_required
@RequerPermissao('XML_ECOBOX.SINCRONIZAR')
def uploadLocal():
    arquivos = request.files.getlist("arquivos")

    if not arquivos:
        flash("Nenhum ficheiro selecionado para transferir.", "erro")
        return redirect(url_for("main.home"))

    df = pd.read_excel("Data/IntParametros.xlsx", sheet_name="XMLsEcobox")
    linha = df.iloc[0].to_dict() 
    parametrosInformacao = {"Saida": linha["Saida"]}

    sucesso, mensagem = TransferenciaService.transferirArquivosLocal(parametrosInformacao, arquivos)
    
    if sucesso:
        flash(mensagem, "sucesso")
    else:
        flash(mensagem, "erro")

    return redirect(url_for("main.home"))

# --- ROTAS DO MÓDULO REINTEGRACAO_WMS ---

@bp.route("/reintegracao")
@login_required
@RequerPermissao('REINTEGRACAO_WMS.VISUALIZAR')
def reintegracao():
    return render_template("Reintegracao.html")

@bp.route("/api/reintegracao/pesquisar", methods=["POST"])
@login_required
@RequerPermissao('REINTEGRACAO_WMS.VISUALIZAR')
def apiReintegracaoPesquisar():
    cliente = request.form.get("cliente")
    filtro = request.form.get("filtro", "").strip()

    parametros = ExcelService.carregarParametrosReintegracao(cliente)
    if not parametros:
        return jsonify({"status": "erro", "mensagem": "Cliente não encontrado"}), 400

    arquivos = SftpService.listarArquivosSeguro(parametros, filtro)
    return jsonify({"status": "ok", "arquivos": arquivos})

@bp.route("/api/reintegracao/transferir", methods=["POST"])
@login_required
@RequerPermissao('REINTEGRACAO_WMS.SINCRONIZAR')
def apiReintegracaoTransferir():
    cliente = request.form.get("cliente")
    arquivosCombinados = request.form.getlist("arquivos")    

    if not cliente or not arquivosCombinados:
        return jsonify({"status": "erro", "mensagem": "Cliente e ficheiros são obrigatórios"}), 400

    parametros = ExcelService.carregarParametrosReintegracao(cliente)
    if not parametros:
        return jsonify({"status": "erro", "mensagem": "Cliente não encontrado"}), 400

    resultados = SftpService.transferirArquivosSftp(parametros, arquivosCombinados)
    
    return jsonify({"status": "ok", "resultados": resultados})

@bp.route("/api/clientes", methods=["GET"])
@login_required
@RequerPermissao('REINTEGRACAO_WMS.VISUALIZAR')
def apiClientes():
    clientes = ExcelService.carregarClientes('Teste')
    if (clientes.any()):
        return jsonify(clientes.tolist())
    return jsonify({"erro": "Nenhum Cliente Parametrizado para Reintegração"}), 404

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("main.index"))