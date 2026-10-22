/**
 * WolfAnalytics Client SDK (v1.0.0)
 * Gobernanza: Límite estricto < 150 líneas.
 */
(function () {
    "use strict";

    const scriptTag = document.currentScript || document.querySelector('script[data-site-key]');
    if (!scriptTag) return;

    const siteKey = scriptTag.getAttribute('data-site-key');
    if (!siteKey) {
        console.error("WolfAnalytics: Falta la Site Key. El SDK está bloqueado.");
        return;
    }

    const API_BASE = scriptTag.getAttribute('data-api-base') || 'http://127.0.0.1:5000/api/v1';

    // 1. EL HANDSHAKE: Validar la llave contra la API antes de activar el SDK
    fetch(API_BASE + '/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ site_key: siteKey })
    })
    .then(function(res) {
        return res.json().then(function(data) {
            return { ok: res.ok, status: res.status, data: data };
        });
    })
    .then(function(result) {
        if (!result.ok || !result.data.valid) {
            console.warn("WolfAnalytics: SDK Bloqueado ->", result.data.error || "Licencia inactiva.");
            return; // BLOQUEO TOTAL: El SDK finaliza inmediatamente sin activar listeners
        }

        console.info("WolfAnalytics: Licencia válida. Iniciando recolección para:", result.data.domain);
        initializeTracker(siteKey, API_BASE);
    })
    .catch(function(err) {
        console.error("WolfAnalytics: No se pudo conectar con el servidor de licencias.", err);
    });

    // 2. MOTOR DE RECOLECCIÓN (Solo se ejecuta si la llave fue aprobada)
    function initializeTracker(key, apiBase) {
        const eventsBuffer = [];

        // Registrar visita inicial (Pageview)
        eventsBuffer.push({
            type: 'pageview',
            target: document.title || 'Page',
            url: window.location.href
        });

        // Interceptar clics en elementos interactivos
        document.addEventListener('click', function(e) {
            const targetEl = e.target;
            const identifier = targetEl.tagName + (targetEl.id ? '#' + targetEl.id : '') +
                (targetEl.className ? '.' + targetEl.className.split(' ')[0] : '');

            eventsBuffer.push({
                type: 'click',
                target: identifier,
                url: window.location.href
            });
        }, true);

        // Envío seguro antes de abandonar la página (sendBeacon / fetch keepalive)
        function flushEvents() {
            if (eventsBuffer.length === 0) return;
            const payload = JSON.stringify({ site_key: key, events: eventsBuffer });
            const endpoint = apiBase + '/telemetry';

            if (navigator.sendBeacon) {
                const blob = new Blob([payload], { type: 'text/plain' });
                navigator.sendBeacon(endpoint, blob);
            } else {
                fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: payload,
                    keepalive: true
                });
            }
        }

        window.addEventListener('visibilitychange', function() {
            if (document.visibilityState === 'hidden') flushEvents();
        });
        window.addEventListener('pagehide', flushEvents);
        window.addEventListener('beforeunload', flushEvents);

        // Actualizar dinámicamente el badge si existe en pantalla
        fetch(apiBase + '/stats/' + encodeURIComponent(key))
            .then(function(res) { return res.json(); })
            .then(function(data) {
                const counterBadge = document.getElementById('wc-number');
                if (counterBadge && typeof data.total_events === 'number') {
                    counterBadge.textContent = data.total_events;
                }
            })
            .catch(function() {});
    }
})();
