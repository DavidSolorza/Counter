/**
 * WolfAnalytics Enterprise SDK (v2.0.0 - Standalone Unified Bundle)
 * Gobernanza: Límite estricto < 150 líneas.
 */
(function () {
    "use strict";

    const tag = document.currentScript || document.querySelector('script[data-site-key]');
    if (!tag) return;

    const key = tag.getAttribute('data-site-key');
    if (!key) {
        console.error("WolfAnalytics: Falta la Site Key. SDK bloqueado.");
        return;
    }

    const API_BASE = tag.getAttribute('data-api-base') || 'http://127.0.0.1:5000/api/v1';

    // 1. Handshake de activación
    fetch(API_BASE + '/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ site_key: key })
    })
    .then(r => r.json())
    .then(function(res) {
        if (!res.valid) {
            console.warn("WolfAnalytics: Licencia inactiva o bloqueada.");
            return;
        }
        console.info("WolfAnalytics Enterprise activo para:", res.domain);
        boot(key, API_BASE);
    })
    .catch(function(err) {
        console.error("WolfAnalytics: Error al conectar con el servidor de licencias.", err);
    });

    function boot(siteKey, apiBase) {
        const buffer = [];
        let startTime = Date.now();
        let dwellMs = 0;
        let isVis = document.visibilityState === 'visible';

        function emit(type, data) {
            buffer.push({ event_type: type, page_url: window.location.href, event_data: data || {} });
        }

        function flush() {
            if (buffer.length === 0) return;
            const payload = JSON.stringify({ site_key: siteKey, events: buffer.splice(0, buffer.length) });
            const endpoint = apiBase + '/telemetry';
            if (navigator.sendBeacon) {
                navigator.sendBeacon(endpoint, new Blob([payload], { type: 'text/plain' }));
            } else {
                fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: payload, keepalive: true });
            }
        }

        // Visibilidad y Permanencia Real
        document.addEventListener('visibilitychange', function() {
            if (document.visibilityState === 'visible') { startTime = Date.now(); isVis = true; }
            else { if (isVis) dwellMs += Date.now() - startTime; isVis = false; flush(); }
        });
        window.addEventListener('pagehide', flush);
        window.addEventListener('beforeunload', function() {
            const activeTime = isVis ? dwellMs + (Date.now() - startTime) : dwellMs;
            emit('page_dwell', { active_dwell_ms: activeTime });
            flush();
        });

        // Métricas de Performance Web Vitals
        window.addEventListener('load', function() {
            setTimeout(function() {
                const nav = performance.getEntriesByType ? performance.getEntriesByType('navigation')[0] : null;
                emit('web_vitals', {
                    ttfb_ms: nav ? Math.round(nav.responseStart - nav.requestStart) : 0,
                    load_time_ms: nav ? Math.round(nav.loadEventEnd - nav.startTime) : 0,
                    dom_ready_ms: nav ? Math.round(nav.domInteractive - nav.startTime) : 0
                });
                flush();
            }, 100);
        });

        // Centinela de Errores Frontend
        window.addEventListener('error', function(e) {
            emit('client_error', { message: e.message, file: e.filename, line: e.lineno, stack: e.error ? e.error.stack : null });
            flush();
        });
        window.addEventListener('unhandledrejection', function(e) {
            emit('promise_rejection', { reason: String(e.reason) });
            flush();
        });

        // Captura de clics en DOM
        document.addEventListener('click', function(e) {
            const el = e.target;
            const id = el.tagName + (el.id ? '#' + el.id : '') + (el.className ? '.' + String(el.className).split(' ')[0] : '');
            emit('click', { element: id, text: (el.innerText || '').slice(0, 40).trim(), dataset: Object.assign({}, el.dataset) });
        }, true);

        // API Pública
        window.WolfAnalytics = {
            track: function(t, d) { emit(t, d); },
            flush: flush
        };

        // Actualizar badge visual si existe
        fetch(apiBase + '/stats/' + encodeURIComponent(siteKey))
            .then(r => r.json())
            .then(d => { const b = document.getElementById('wc-number'); if (b && typeof d.total_events === 'number') b.textContent = d.total_events; })
            .catch(function() {});
    }
})();
