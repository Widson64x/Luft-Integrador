/* ==========================================================================
   EDI-INTEGRADOR - BASE JAVASCRIPT
   Script base carregado em todas as páginas do sistema.
   ========================================================================== */

// Sempre iniciar com a sidebar fechada
(function() {
    const sidebar = document.getElementById('luft-sidebar');

    if (sidebar && !sidebar.classList.contains('collapsed')) {
        sidebar.classList.add('collapsed');
    } else {
        console.log('[Base.js] Sidebar já estava fechada ou não encontrada.');
    }

    localStorage.setItem('luft-sidebar-collapsed', 'true');
    console.log('[Base.js] localStorage atualizado.');
})();
