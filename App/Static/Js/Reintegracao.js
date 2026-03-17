class ReintegracaoWMS {
    constructor() {
        this.formPesquisa = document.getElementById('formPesquisa');
        this.selectCliente = document.getElementById('selectCliente');
        this.inputFiltro = document.getElementById('inputFiltro');
        this.containerResultados = document.getElementById('containerResultados');
        this.tabelaCorpo = document.getElementById('tabelaArquivosCorpo');
        this.btnTransferir = document.getElementById('btnTransferir');
        this.checkTodos = document.getElementById('checkTodos');

        this.arquivosEncontrados = [];

        this.inicializar();
    }

    async inicializar() {
        await this.carregarClientes();
        this.registrarEventos();
    }

    async carregarClientes() {
        try {
            // Usando a variável API do BaseLayout.html
            const resposta = await fetch(API.clientes);
            const clientes = await resposta.json();
            
            this.selectCliente.innerHTML = '<option value="">Selecione um Cliente...</option>';
            clientes.forEach(cliente => {
                const opt = document.createElement('option');
                opt.value = cliente;
                opt.textContent = cliente;
                this.selectCliente.appendChild(opt);
            });
        } catch (erro) {
            console.error("Erro ao buscar clientes:", erro);
            this.selectCliente.innerHTML = '<option value="">Erro ao carregar</option>';
        }
    }

    registrarEventos() {
        this.formPesquisa.addEventListener('submit', (e) => this.pesquisarArquivos(e));
        
        this.checkTodos.addEventListener('change', (e) => {
            const checkboxes = this.tabelaCorpo.querySelectorAll('.check-arquivo');
            checkboxes.forEach(cb => cb.checked = e.target.checked);
            this.atualizarBotaoTransferir();
        });

        this.btnTransferir.addEventListener('click', () => this.transferirSelecionados());
    }

    async pesquisarArquivos(evento) {
        evento.preventDefault();
        const formData = new FormData();
        formData.append('cliente', this.selectCliente.value);
        formData.append('filtro', this.inputFiltro.value);

        try {
            const resposta = await fetch(API.pesquisar, {
                method: 'POST',
                body: formData
            });
            const dados = await resposta.json();

            if (dados.status === 'ok') {
                this.arquivosEncontrados = dados.arquivos;
                this.renderizarTabela();
            } else {
                alert("Erro: " + dados.mensagem);
            }
        } catch (erro) {
            console.error("Erro na pesquisa:", erro);
        }
    }

    renderizarTabela() {
        // Atualiza a badge de contagem
        document.getElementById('badgeContador').textContent = `${this.arquivosEncontrados.length} arquivos`;
        
        this.tabelaCorpo.innerHTML = '';
        this.checkTodos.checked = false;
        this.btnTransferir.disabled = true;

        if (this.arquivosEncontrados.length === 0) {
            // Se não encontrar nada, injeta o Empty State lindo
            this.tabelaCorpo.innerHTML = `
                <tr id="linhaVazia">
                    <td colspan="4" class="text-center text-muted" style="padding: 4rem 1rem;">
                        <i class="ph-thin ph-warning-circle text-warning" style="font-size: 4rem; opacity: 0.5;"></i>
                        <h5 class="mt-3 mb-1 font-bold">Nenhum arquivo encontrado</h5>
                        <p class="mb-0 text-sm">Tente ajustar o filtro e busque novamente.</p>
                    </td>
                </tr>
            `;
            return;
        }

        this.arquivosEncontrados.forEach((arq, index) => {
            const valorArquivo = `${arq.diretorio_origem}|${arq.nome}`;
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="text-center"><input type="checkbox" class="check-arquivo" value="${valorArquivo}" data-index="${index}"></td>
                <td class="font-weight-medium">${arq.nome}</td>
                <td><span class="luft-badge luft-badge-secondary">${arq.tamanho}</span></td>
                <td class="text-muted text-sm">${arq.data}</td>
            `;
            
            const checkbox = tr.querySelector('.check-arquivo');
            checkbox.addEventListener('change', () => this.atualizarBotaoTransferir());
            
            this.tabelaCorpo.appendChild(tr);
        });
    }

    atualizarBotaoTransferir() {
        const selecionados = this.tabelaCorpo.querySelectorAll('.check-arquivo:checked');
        this.btnTransferir.disabled = selecionados.length === 0;
        this.btnTransferir.textContent = selecionados.length > 0 
            ? `Transferir Selecionados (${selecionados.length})` 
            : 'Transferir Selecionados';
    }

    async transferirSelecionados() {
        const selecionados = Array.from(this.tabelaCorpo.querySelectorAll('.check-arquivo:checked'))
                                  .map(cb => cb.value);

        if (selecionados.length === 0) return;

        this.btnTransferir.disabled = true;
        this.btnTransferir.textContent = "Transferindo...";

        const formData = new FormData();
        formData.append('cliente', this.selectCliente.value);
        selecionados.forEach(arq => formData.append('arquivos', arq));

        try {
            const resposta = await fetch(API.transferir, {
                method: 'POST',
                body: formData
            });
            const dados = await resposta.json();

            if (dados.status === 'ok') {
                alert('Transferência concluída!');
                // Refaz a pesquisa para atualizar a lista
                this.formPesquisa.dispatchEvent(new Event('submit'));
            } else {
                alert("Erro: " + dados.mensagem);
                this.btnTransferir.disabled = false;
            }
        } catch (erro) {
            console.error("Erro na transferência:", erro);
            this.btnTransferir.disabled = false;
        }
    }
}

document.addEventListener('DOMContentLoaded', () => new ReintegracaoWMS());