// Service Worker — cache shell for offline launch from home screen
const CACHE = "voice-input-v3";
const SHELL = ["/", "/manifest.json", "/icons/icon-192.png", "/vendor/socket.io.min.js"];

self.addEventListener("install", e =>
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)))
);

self.addEventListener("activate", e =>
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  )
);

self.addEventListener("fetch", e => {
  // Network first, fallback to cache
  e.respondWith(
    fetch(e.request).catch(() => caches.match(e.request))
  );
});
