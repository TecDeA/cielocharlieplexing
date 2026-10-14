/* Service Worker - Simulador de Charlieplexing */

// Versión de la aplicación: fuente única de verdad.
// Cualquier cambio aquí se refleja automáticamente en el chip del título.
const VERSION = 'v2.3';
const CACHE_NAME = `charlieplexing-${VERSION}`;
const ASSETS = [
    './',
    './index.html',
    './manifest.webmanifest',
    './favicon.ico',
    './icons/icon-192.png',
    './icons/icon-512.png',
    './icons/icon-maskable-192.png',
    './icons/icon-maskable-512.png',
    './icons/apple-touch-icon.png'
];

// Instalación: precachear la aplicación completa para funcionar offline
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(ASSETS))
            .then(() => self.skipWaiting())
    );
});

// Activación: limpiar cachés antiguas
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(
                keys
                    .filter((key) => key !== CACHE_NAME && key.startsWith('charlieplexing-'))
                    .map((key) => caches.delete(key))
            ).then(() => self.clients.claim())
        )
    );
});

// Comunicación con el cliente: permite consultar la versión dinámicamente
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'GET_VERSION') {
        // Responde por el mismo canal (MessageChannel) para garantizar la entrega
        const reply = { type: 'VERSION', version: VERSION };
        if (event.ports && event.ports[0]) {
            event.ports[0].postMessage(reply);
        } else if (event.source) {
            event.source.postMessage(reply);
        }
    }
});

// Estrategia cache-first con actualización en segundo plano
self.addEventListener('fetch', (event) => {
    if (event.request.method !== 'GET') return;

    event.respondWith(
        caches.match(event.request).then((cached) => {
            const fetched = fetch(event.request)
                .then((response) => {
                    if (response && response.status === 200 && response.type === 'basic') {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
                    }
                    return response;
                })
                .catch(() => cached);

            return cached || fetched;
        })
    );
});
