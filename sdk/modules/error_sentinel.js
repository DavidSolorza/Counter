/**
 * sdk/modules/error_sentinel.js
 * Centinela de captura de errores de JavaScript y promesas rechazadas.
 * Gobernanza: Límite estricto < 150 líneas.
 */
export function initErrorSentinel(onError) {
    window.addEventListener('error', function(event) {
        if (typeof onError !== 'function') return;
        onError({
            category: 'javascript_error',
            message: event.message || 'Unknown error',
            filename: event.filename || null,
            lineno: event.lineno || 0,
            colno: event.colno || 0,
            stack: event.error && event.error.stack ? event.error.stack.slice(0, 300) : null
        });
    });

    window.addEventListener('unhandledrejection', function(event) {
        if (typeof onError !== 'function') return;
        const reason = event.reason;
        onError({
            category: 'unhandled_rejection',
            message: reason ? (reason.message || String(reason)) : 'Promise rejected',
            stack: reason && reason.stack ? reason.stack.slice(0, 300) : null
        });
    });
}
