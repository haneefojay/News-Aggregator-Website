const CACHE_NAME = 'pulse-news-v1';
const ASSETS_TO_CACHE = [
    './',
    './index.html',
    './style.css',
    './app.js',
    './icon.png',
    './manifest.json',
    'https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Outfit:wght@300;400;500;600;700&display=swap',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css'
];

// Install Event: Cache core assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Opened cache');
                return cache.addAll(ASSETS_TO_CACHE);
            })
    );
});

// Activate Event: Clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Fetch Event: network-first strategy for API, cache-first for static assets
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // If it's an API call, go network only (we want fresh news)
    if (url.pathname.includes('/api/v1')) {
        return;
    }

    // For other requests (static assets), try cache first, then network
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Cache hit - return response
                if (response) {
                    return response;
                }
                return fetch(event.request);
            })
    );
});
