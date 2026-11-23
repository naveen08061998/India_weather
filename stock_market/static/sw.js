/**
 * Indian Stock Market — Service Worker
 * App shell → cache-first, update in background. Everything else (API/CDN) → network-only.
 */

const CACHE_VERSION = "stocks-v1";
const SHELL_CACHE = `${CACHE_VERSION}-shell`;

const SHELL_URLS = [
    "./",
    "./manifest.json",
    "./static/icon-192.png",
    "./static/icon-512.png",
];

self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(SHELL_CACHE).then(cache => cache.addAll(SHELL_URLS))
    );
    self.skipWaiting();
});

self.addEventListener("activate", event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys.filter(k => k.startsWith("stocks-") && k !== SHELL_CACHE)
                    .map(k => caches.delete(k))
            )
        )
    );
    self.clients.claim();
});

self.addEventListener("fetch", event => {
    const url = new URL(event.request.url);
    if (event.request.method !== "GET") return;
    if (!url.protocol.startsWith("http")) return;
    if (url.hostname !== self.location.hostname) return; // fonts/CDNs/external APIs → network-only

    event.respondWith(
        caches.match(event.request).then(cached => {
            const fetchPromise = fetch(event.request)
                .then(response => {
                    if (response.ok) {
                        const clone = response.clone();
                        caches.open(SHELL_CACHE).then(c => c.put(event.request, clone));
                    }
                    return response;
                })
                .catch(() => cached);
            return cached || fetchPromise;
        })
    );
});
