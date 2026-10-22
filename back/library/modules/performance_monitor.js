/**
 * sdk/modules/performance_monitor.js
 * Extracción de métricas web mediante Navigation Timing y Performance API.
 * Gobernanza: Límite estricto < 150 líneas.
 */
export function capturePerformanceMetrics(callback) {
    function calculate() {
        if (!window.performance) return;

        const navEntries = performance.getEntriesByType('navigation');
        let metrics = {};

        if (navEntries && navEntries.length > 0) {
            const nav = navEntries[0];
            metrics = {
                dns_time_ms: Math.round(nav.domainLookupEnd - nav.domainLookupStart),
                ttfb_ms: Math.round(nav.responseStart - nav.requestStart),
                dom_interactive_ms: Math.round(nav.domInteractive - nav.startTime),
                total_load_ms: Math.round(nav.loadEventEnd - nav.startTime)
            };
        } else if (performance.timing) {
            const t = performance.timing;
            metrics = {
                dns_time_ms: Math.max(0, t.domainLookupEnd - t.domainLookupStart),
                ttfb_ms: Math.max(0, t.responseStart - t.requestStart),
                dom_interactive_ms: Math.max(0, t.domInteractive - t.navigationStart),
                total_load_ms: Math.max(0, t.loadEventEnd - t.navigationStart)
            };
        }

        if (typeof callback === 'function') {
            callback(metrics);
        }
    }

    if (document.readyState === 'complete') {
        setTimeout(calculate, 0);
    } else {
        window.addEventListener('load', function() {
            setTimeout(calculate, 0);
        }, { once: true });
    }
}
