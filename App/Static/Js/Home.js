class EcoboxProcesso {
    constructor() {
        this.inputArquivos = document.getElementById('arquivos');
        this.dropzone = document.getElementById('dropzoneEcobox');
        this.divLista = document.getElementById('listaArquivos');
        this.fileSection = document.getElementById('uploadFileSection');
        this.badgeCount = document.getElementById('badgeUploadCount');
        this.btnSubmit = document.getElementById('btnTransferirLocal');
        this.btnLimpar = document.getElementById('btnLimparArquivos');

        // DataTransfer para manter a lista mutável de arquivos
        this.dataTransfer = new DataTransfer();

        this.inicializarEventos();
    }

    inicializarEventos() {
        if (!this.inputArquivos || !this.dropzone) return;

        // Seleção via input
        this.inputArquivos.addEventListener('change', () => {
            this.adicionarArquivos(this.inputArquivos.files);
        });

        // Drag & Drop
        this.dropzone.addEventListener('dragenter', (e) => this.onDragEnter(e));
        this.dropzone.addEventListener('dragover', (e) => this.onDragOver(e));
        this.dropzone.addEventListener('dragleave', (e) => this.onDragLeave(e));
        this.dropzone.addEventListener('drop', (e) => this.onDrop(e));

        // Botão Limpar
        this.btnLimpar.addEventListener('click', () => this.limparTudo());
    }

    // --- Drag & Drop ---
    onDragEnter(e) {
        e.preventDefault();
        this.dropzone.classList.add('drag-over');
    }

    onDragOver(e) {
        e.preventDefault();
        this.dropzone.classList.add('drag-over');
    }

    onDragLeave(e) {
        e.preventDefault();
        // Evita flicker quando o drag sai de elementos filhos
        if (!this.dropzone.contains(e.relatedTarget)) {
            this.dropzone.classList.remove('drag-over');
        }
    }

    onDrop(e) {
        e.preventDefault();
        this.dropzone.classList.remove('drag-over');
        if (e.dataTransfer.files.length > 0) {
            this.adicionarArquivos(e.dataTransfer.files);
        }
    }

    // --- Gerenciamento de Arquivos ---
    adicionarArquivos(novosArquivos) {
        Array.from(novosArquivos).forEach(arq => {
            // Aceita apenas .xml
            if (!arq.name.toLowerCase().endsWith('.xml')) return;

            // Evita duplicatas pelo nome
            const jaExiste = Array.from(this.dataTransfer.files).some(f => f.name === arq.name);
            if (!jaExiste) {
                this.dataTransfer.items.add(arq);
            }
        });

        // Sincroniza o input nativo com a lista atualizada
        this.inputArquivos.files = this.dataTransfer.files;
        this.renderizar();
    }

    removerArquivo(index) {
        this.dataTransfer.items.remove(index);
        this.inputArquivos.files = this.dataTransfer.files;
        this.renderizar();
    }

    limparTudo() {
        this.dataTransfer = new DataTransfer();
        this.inputArquivos.files = this.dataTransfer.files;
        this.renderizar();
    }

    // --- Renderização ---
    renderizar() {
        const arquivos = Array.from(this.dataTransfer.files);
        const total = arquivos.length;

        // Atualiza badge e botão
        this.badgeCount.textContent = total;
        this.btnSubmit.disabled = total === 0;
        this.btnLimpar.style.display = total > 0 ? '' : 'none';

        // Mostra/esconde seção
        if (total === 0) {
            this.fileSection.classList.add('d-none');
            this.divLista.innerHTML = '';
            return;
        }

        this.fileSection.classList.remove('d-none');

        // Renderiza cards de arquivos
        this.divLista.innerHTML = arquivos.map((arq, i) => `
            <div class="upload-file-item">
                <div class="upload-file-icon">
                    <i class="ph ph-file-xml"></i>
                </div>
                <div class="upload-file-info">
                    <span class="upload-file-name" title="${arq.name}">${arq.name}</span>
                    <span class="upload-file-size">${this.formatarTamanho(arq.size)}</span>
                </div>
                <button type="button" class="upload-file-remove" data-index="${i}" title="Remover">
                    <i class="ph ph-x"></i>
                </button>
            </div>
        `).join('');

        // Event listeners nos botões de remover
        this.divLista.querySelectorAll('.upload-file-remove').forEach(btn => {
            btn.addEventListener('click', () => {
                this.removerArquivo(parseInt(btn.dataset.index));
            });
        });
    }

    formatarTamanho(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / 1048576).toFixed(1) + ' MB';
    }
}

// Inicia a classe quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => new EcoboxProcesso());