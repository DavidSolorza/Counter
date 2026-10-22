/**
 * Counter Analytics Enterprise SDK (v3.0.0 - Passive Telemetry & Friction Shield)
 * Gobernanza: Límite estricto < 150 líneas.
 */
(function () {
    "use strict";
    try {
        const tag = document.currentScript || document.querySelector('script[data-site-key]');
        if (!tag) return;
        const key = tag.getAttribute('data-site-key');
        if (!key) return;

        const isDebug = tag.getAttribute('data-debug') === 'true';
        const API = tag.getAttribute('data-api-base') || 'http://127.0.0.1:5000/api/v1';
        const log = (m, d) => { if (isDebug) console.log("%c[Counter] " + m, "color: #22c55e; font-weight: bold;", d || ""); };

        // Sesión efímera y atribución UTM
        let sid = sessionStorage.getItem('__cntr_sid');
        if (!sid) { sid = Math.random().toString(36).slice(2, 9) + Date.now().toString(36); sessionStorage.setItem('__cntr_sid', sid); }
        const p = new URLSearchParams(window.location.search);
        const utm = { src: p.get('utm_source'), med: p.get('utm_medium'), camp: p.get('utm_campaign'), ref: document.referrer || null };

        function isPii(el) {
            if (!el) return false;
            const t = (el.type || '').toLowerCase(), n = (el.name || el.id || '').toLowerCase();
            return t === 'password' || el.hasAttribute('data-private') || /password|card|cvv|token|secret/i.test(n);
        }

        fetch(API + '/verify', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ site_key: key }) })
            .then(r => r.json()).then(res => { if (res.valid) boot(key, API); }).catch(() => {});

        function boot(siteKey, apiBase) {
            const buf = [];
            let tStart = Date.now(), dwell = 0, isVis = document.visibilityState === 'visible', debTimer = null;
            const recentClicks = [];
            const milestones = { '25%': false, '50%': false, '75%': false, '100%': false };

            function emit(t, d, imm) {
                try {
                    const data = Object.assign({ _sid: sid }, d);
                    buf.push({ event_type: t, page_url: window.location.href, event_data: data });
                    log("Capturado (" + t + "):", data);
                    if (imm) flush(); else { clearTimeout(debTimer); debTimer = setTimeout(flush, 1200); }
                } catch(e) {}
            }

            function flush() {
                try {
                    if (buf.length === 0) return;
                    const batch = buf.splice(0, buf.length), payload = JSON.stringify({ site_key: siteKey, events: batch });
                    const ep = apiBase + '/telemetry';
                    if (navigator.sendBeacon && document.visibilityState === 'hidden') {
                        navigator.sendBeacon(ep, new Blob([payload], { type: 'text/plain' }));
                    } else {
                        fetch(ep, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: payload, keepalive: true }).catch(() => {});
                    }
                } catch(e) {}
            }

            setInterval(flush, 4000);

            // Scroll pasivo ultra-optimizado (Compositor 60 FPS)
            window.addEventListener('scroll', function() {
                const max = document.documentElement.scrollHeight - window.innerHeight;
                if (max <= 0) return;
                const pct = Math.round((window.scrollY / max) * 100);
                ['25%', '50%', '75%', '100%'].forEach(m => {
                    const threshold = parseInt(m);
                    if (pct >= threshold && !milestones[m]) { milestones[m] = true; emit('scroll_milestone', { depth: m }); }
                });
            }, { passive: true });

            // Clics y Detección de Fricción (Rage Clicks)
            document.addEventListener('click', function(e) {
                const el = e.target, now = Date.now();
                const id = el.tagName + (el.id ? '#' + el.id : '') + (el.className ? '.' + String(el.className).split(' ')[0] : '');
                recentClicks.push({ id: id, time: now });
                if (recentClicks.length > 4) recentClicks.shift();

                const isRage = recentClicks.length >= 3 && (now - recentClicks[0].time < 800) && recentClicks.every(c => c.id === id);
                const text = isPii(el) ? '[REDACTED_PII]' : (el.innerText || '').slice(0, 35).trim();

                if (isRage) emit('rage_click', { element: id, text: text, clicks: recentClicks.length }, true);
                else emit('click', { element: id, text: text });
            }, true);

            // Ciclo de vida y Web Vitals
            window.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') { tStart = Date.now(); isVis = true; } else { if (isVis) dwell += Date.now() - tStart; isVis = false; flush(); } });
            window.addEventListener('beforeunload', () => { emit('page_dwell', { active_dwell_ms: isVis ? dwell + (Date.now() - tStart) : dwell }); flush(); });
            window.addEventListener('load', () => setTimeout(() => {
                const n = performance.getEntriesByType ? performance.getEntriesByType('navigation')[0] : null;
                const conn = navigator.connection || {};
                emit('web_vitals', { ttfb_ms: n ? Math.round(n.responseStart - n.requestStart) : 0, load_ms: n ? Math.round(n.loadEventEnd - n.startTime) : 0, net: conn.effectiveType || 'wifi', utm: utm }, false);
            }, 100));

            window.addEventListener('error', e => emit('client_error', { message: e.message, file: e.filename, line: e.lineno }, true));
            window.Counter = window.WolfAnalytics = { track: (t, d, imm) => emit(t, d, imm), flush: flush };
        }
    } catch (e) {}
})();
