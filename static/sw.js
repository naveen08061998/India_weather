/**
 * India Weather PWA — Service Worker
 * ====================================
 * Strategy:
 *   - App shell (HTML/JS/CSS)  → Cache-first, update in background
 *   - API calls (/api/*)       → Network-first, fall back to cache
 *   - External weather APIs    → Network-only (no stale weather data)
 *   - Push notifications       → Show alert with district name + label
 */

const CACHE_VERSION = "india-wx-v1";
const SHELL_CACHE = `${CACHE_VERSION}-shell`;
const DATA_CACHE = `${CACHE_VERSION}-data`;

// App-shell resources to pre-cache on install
const SHELL_URLS = [
    "/",
    "/manifest.json",
    "/static/icon-192.png",
    "/static/icon-512.png",
];

// ── Install: cache app shell ──────────────────────────────────────────────
self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(SHELL_CACHE).then(cache => cache.addAll(SHELL_URLS))
    );
    self.skipWaiting();
});

// ── Activate: purge old caches ────────────────────────────────────────────
self.addEventListener("activate", event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys
                    .filter(k => k.startsWith("india-wx-") && k !== SHELL_CACHE && k !== DATA_CACHE)
                    .map(k => caches.delete(k))
            )
        )
    );
    self.clients.claim();
});

// ── Fetch: routing strategy ───────────────────────────────────────────────
self.addEventListener("fetch", event => {
    const url = new URL(event.request.url);

    // Skip non-GET and chrome-extension requests
    if (event.request.method !== "GET") return;
    if (!url.protocol.startsWith("http")) return;

    // External weather APIs → network-only (always fresh)
    const isExternal = url.hostname !== self.location.hostname;
    if (isExternal) {
        event.respondWith(fetch(event.request));
        return;
    }

    // /api/* → network-first, fall back to cached response
    if (url.pathname.startsWith("/api/")) {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    if (response.ok) {
                        const clone = response.clone();
                        caches.open(DATA_CACHE).then(c => c.put(event.request, clone));
                    }
                    return response;
                })
                .catch(() => caches.match(event.request))
        );
        return;
    }

    // App shell → cache-first, revalidate in background
    event.respondWith(
        caches.match(event.request).then(cached => {
            const networkFetch = fetch(event.request).then(response => {
                if (response.ok) {
                    const clone = response.clone();
                    caches.open(SHELL_CACHE).then(c => c.put(event.request, clone));
                }
                return response;
            });
            return cached || networkFetch;
        })
    );
});

// ── Push notifications ────────────────────────────────────────────────────
self.addEventListener("push", event => {
    let data = { title: "India Weather Alert", body: "New weather alert", icon: "/static/icon-192.png" };
    try { data = { ...data, ...event.data.json() }; } catch (_) { }

    event.waitUntil(
        self.registration.showNotification(data.title, {
            body: data.body,
            icon: data.icon || "/static/icon-192.png",
            badge: "/static/icon-192.png",
            tag: "weather-alert",
            renotify: true,
            data: { url: data.url || "/" },
        })
    );
});

self.addEventListener("notificationclick", event => {
    event.notification.close();
    const target = event.notification.data?.url || "/";
    event.waitUntil(
        clients.matchAll({ type: "window", includeUncontrolled: true }).then(list => {
            const existing = list.find(c => c.url.includes(self.location.origin));
            if (existing) return existing.focus();
            return clients.openWindow(target);
        })
    );
});
