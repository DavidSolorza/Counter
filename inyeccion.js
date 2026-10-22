// Función dentro de tu librería para inyectar la línea legal y de anuncios al fondo
function injectMicroFooter() {
    if (document.getElementById('wolf-legal-banner')) return; // Evitar duplicados

    const footerBanner = document.createElement('div');
    footerBanner.id = 'wolf-legal-banner';
    
    // Estilos para que sea una línea extremadamente fina, abajo del todo, legible pero discreta
    footerBanner.innerHTML = `
        <div style="
            position: relative;
            width: 100%;
            padding: 3px 0;
            background: transparent;
            border-top: 1px solid rgba(128, 128, 128, 0.15);
            text-align: center;
            font-family: system-ui, -apple-system, sans-serif;
            font-size: 10px;
            color: inherit;
            opacity: 0.4;
            display: flex;
            justify-content: center;
            gap: 12px;
            z-index: 9999;
            pointer-events: auto;
        ">
            <span>Stats by <a href="https://servidor.blog" target="_blank" style="color: inherit; text-decoration: underline;">WolfStats</a></span>
            <span>•</span>
            <a href="https://servidor.blog/ads" target="_blank" style="color: inherit; text-decoration: none;">Patrocinadores</a>
        </div>
    `;

    // Lo metemos justo antes de cerrar el body de la página del cliente
    document.body.appendChild(footerBanner);
}