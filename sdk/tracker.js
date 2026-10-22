/**
 * WolfAnalytics Enterprise SDK (v2.1.0 - Realtime Interval + Debounce + Debug)
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

    const isDebug = tag.getAttribute('data-debug') === 'true';
    const API_BASE = tag.getAttribute('data-api-base') || 'http://127.0.0.1:5000/api/v1';

    function debugLog(label, data) {
        if (isDebug) console.log("%c[WolfAnalytics] " + label, "color: #22c55e; font-weight: bold;", data || "");
    }

    // 1. Handshake inicial
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
        debugLog("Desbloqueado para dominio:", res.domain);
        boot(key, API_BASE);
    })
    .catch(function(err) {
        console.error("WolfAnalytics: Error conectando con el servidor.", err);
    });

    function boot(siteKey, apiBase) {
        const buffer = [];
        let startTime = Date.now(), dwellMs = 0, isVis = document.visibilityState === 'visible';
        let debounceTimer = null;

        function emit(type, data, immediate) {
            buffer.push({ event_type: type, page_url: window.location.href, event_data: data || {} });
            debugLog("Capturado (" + type + "):", data);

            if (immediate) {
                flush();
            } else {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(flush, 1200);
            }
        }

        function flush() {
            if (buffer.length === 0) return;
            const batch = buffer.splice(0, buffer.length);
            const payload = JSON.stringify({ site_key: siteKey, events: batch });
            const endpoint = apiBase + '/telemetry';
            debugLog("Enviando lote al servidor (" + batch.length + " eventos)...");

            if (navigator.sendBeacon && document.visibilityState === 'hidden') {
                navigator.sendBeacon(endpoint, new Blob([payload], { type: 'text/plain' }));
            } else {
                fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: payload,
                    keepalive: true
                })
                .then(r => r.json())
                .then(d => debugLog("Sincronización confirmada (stored: " + d.stored + ")"))
                .catch(err => debugLog("Error en envío:", err));
            }
        }

        // Temporizador periódico cada 4 segundos
        setInterval(flush, 4000);

        // Control de Visibilidad y Permanencia
        document.addEventListener('visibilitychange', function() {
            if (document.visibilityState === 'visible') { startTime = Date.now(); isVis = true; }
            else { if (isVis) dwellMs += Date.now() - startTime; isVis = false; flush(); }
        });
        window.addEventListener('pagehide', flush);
        window.addEventListener('beforeunload', function() {
            const activeTime = isVis ? dwellMs + (Date.now() - startTime) : dwellMs;
            buffer.push({ event_type: 'page_dwell', page_url: window.location.href, event_data: { active_dwell_ms: activeTime } });
            flush();
        });

        // Métricas de Rendimiento (Web Vitals)
        window.addEventListener('load', function() {
            setTimeout(function() {
                const nav = performance.getEntriesByType ? performance.getEntriesByType('navigation')[0] : null;
                emit('web_vitals', {
                    ttfb_ms: nav ? Math.round(nav.responseStart - nav.requestStart) : 0,
                    load_time_ms: nav ? Math.round(nav.loadEventEnd - nav.startTime) : 0,
                    dom_ready_ms: nav ? Math.round(nav.domInteractive - nav.startTime) : 0
                }, false);
            }, 100);
        });

        // Centinela de Errores Frontend (Envío Inmediato)
        window.addEventListener('error', function(e) {
            emit('client_error', { message: e.message, file: e.filename, line: e.lineno, stack: e.error ? e.error.stack : null }, true);
        });
        window.addEventListener('unhandledrejection', function(e) {
            emit('promise_rejection', { reason: String(e.reason) }, true);
        });

        // Intercepción de clics en el DOM
        document.addEventListener('click', function(e) {
            const el = e.target;
            const id = el.tagName + (el.id ? '#' + el.id : '') + (el.className ? '.' + String(el.className).split(' ')[0] : '');
            emit('click', { element: id, text: (el.innerText || '').slice(0, 40).trim(), dataset: Object.assign({}, el.dataset) });
        }, true);

        // API Global
        window.WolfAnalytics = { track: (t, d, imm) => emit(t, d, imm), flush: flush };
    }
})();
