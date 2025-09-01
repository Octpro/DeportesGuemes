/**
 * Service Worker for Deportes Güemes
 * Provides offline functionality and performance optimizations
 */

const CACHE_NAME = 'deportes-guemes-v1.0.0';
const STATIC_CACHE = 'static-v1.0.0';
const DYNAMIC_CACHE = 'dynamic-v1.0.0';
const IMAGE_CACHE = 'images-v1.0.0';

// Files to cache immediately
const STATIC_FILES = [
    '/',
    '/index.html',
    '/carrito.html',
    '/css/main.css',
    '/JS/main.js',
    '/JS/cache-manager.js',
    '/JS/image-optimizer.js',
    '/JS/menus.js',
    '/JS/enhanced-filters.js',
    '/JS/touch-interactions.js',
    '/JS/carrito.js',
    '/JS/productos.json',
    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.9.1/font/bootstrap-icons.css',
    'https://cdn.jsdelivr.net/npm/toastify-js/src/toastify.min.css'
];

// Network-first resources (always try network first)
const NETWORK_FIRST = [
    '/JS/productos.json'
];

// Cache-first resources (try cache first, fallback to network)
const CACHE_FIRST = [
    '/css/',
    '/JS/',
    '/img/',
    'bootstrap-icons',
    'toastify'
];

// Install event - cache static files
self.addEventListener('install', (event) => {
    console.log('🔧 Service Worker installing...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('📦 Caching static files...');
                return cache.addAll(STATIC_FILES);
            })
            .then(() => {
                console.log('✅ Static files cached successfully');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('❌ Failed to cache static files:', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('🚀 Service Worker activating...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== STATIC_CACHE && 
                            cacheName !== DYNAMIC_CACHE && 
                            cacheName !== IMAGE_CACHE) {
                            console.log('🗑️ Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('✅ Service Worker activated');
                return self.clients.claim();
            })
    );
});

// Fetch event - handle requests with different strategies
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Handle different types of requests
    if (isImageRequest(request)) {
        event.respondWith(handleImageRequest(request));
    } else if (isNetworkFirst(request)) {
        event.respondWith(handleNetworkFirst(request));
    } else if (isCacheFirst(request)) {
        event.respondWith(handleCacheFirst(request));
    } else {
        event.respondWith(handleStaleWhileRevalidate(request));
    }
});

/**
 * Check if request is for an image
 */
function isImageRequest(request) {
    return request.destination === 'image' || 
           request.url.includes('/img/') ||
           /\.(jpg|jpeg|png|gif|webp|svg)$/i.test(request.url);
}

/**
 * Check if request should use network-first strategy
 */
function isNetworkFirst(request) {
    return NETWORK_FIRST.some(pattern => request.url.includes(pattern));
}

/**
 * Check if request should use cache-first strategy
 */
function isCacheFirst(request) {
    return CACHE_FIRST.some(pattern => request.url.includes(pattern));
}

/**
 * Handle image requests with cache-first strategy and compression
 */
async function handleImageRequest(request) {
    try {
        // Try cache first
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Fetch from network
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            // Cache the image
            const cache = await caches.open(IMAGE_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.error('❌ Image request failed:', error);
        
        // Return placeholder image if available
        const placeholder = await caches.match('/img/placeholder.png');
        if (placeholder) {
            return placeholder;
        }
        
        // Return empty response as last resort
        return new Response('', { status: 404 });
    }
}

/**
 * Network-first strategy (for dynamic content like productos.json)
 */
async function handleNetworkFirst(request) {
    try {
        // Try network first
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            // Update cache with fresh data
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('🌐 Network failed, trying cache for:', request.url);
        
        // Fallback to cache
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline page or error response
        return new Response(JSON.stringify({
            error: 'Offline',
            message: 'No hay conexión a internet'
        }), {
            status: 503,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}

/**
 * Cache-first strategy (for static assets)
 */
async function handleCacheFirst(request) {
    try {
        // Try cache first
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Fallback to network
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            // Cache the response
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.error('❌ Cache-first request failed:', error);
        return new Response('', { status: 404 });
    }
}

/**
 * Stale-while-revalidate strategy (for general content)
 */
async function handleStaleWhileRevalidate(request) {
    const cache = await caches.open(DYNAMIC_CACHE);
    const cachedResponse = await cache.match(request);
    
    // Fetch fresh version in background
    const fetchPromise = fetch(request).then((networkResponse) => {
        if (networkResponse.ok) {
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    }).catch(() => {
        // Network failed, return cached version if available
        return cachedResponse;
    });
    
    // Return cached version immediately if available, otherwise wait for network
    return cachedResponse || fetchPromise;
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
    console.log('🔄 Background sync triggered:', event.tag);
    
    if (event.tag === 'cart-sync') {
        event.waitUntil(syncCartData());
    } else if (event.tag === 'analytics-sync') {
        event.waitUntil(syncAnalyticsData());
    }
});

/**
 * Sync cart data when back online
 */
async function syncCartData() {
    try {
        console.log('🛒 Syncing cart data...');
        
        // Get pending cart actions from IndexedDB or localStorage
        const pendingActions = JSON.parse(localStorage.getItem('pending-cart-actions') || '[]');
        
        for (const action of pendingActions) {
            // Process each pending action
            await processPendingCartAction(action);
        }
        
        // Clear pending actions
        localStorage.removeItem('pending-cart-actions');
        
        console.log('✅ Cart data synced successfully');
    } catch (error) {
        console.error('❌ Failed to sync cart data:', error);
    }
}

/**
 * Sync analytics data when back online
 */
async function syncAnalyticsData() {
    try {
        console.log('📊 Syncing analytics data...');
        
        const pendingEvents = JSON.parse(localStorage.getItem('pending-analytics') || '[]');
        
        for (const event of pendingEvents) {
            // Send analytics event
            await sendAnalyticsEvent(event);
        }
        
        localStorage.removeItem('pending-analytics');
        
        console.log('✅ Analytics data synced successfully');
    } catch (error) {
        console.error('❌ Failed to sync analytics data:', error);
    }
}

/**
 * Process pending cart action
 */
async function processPendingCartAction(action) {
    // Implementation would depend on your backend API
    console.log('Processing cart action:', action);
}

/**
 * Send analytics event
 */
async function sendAnalyticsEvent(event) {
    // Implementation would depend on your analytics service
    console.log('Sending analytics event:', event);
}

// Push notification handling
self.addEventListener('push', (event) => {
    console.log('📱 Push notification received');
    
    const options = {
        body: event.data ? event.data.text() : 'Nueva notificación de Deportes Güemes',
        icon: '/img/icon-192.png',
        badge: '/img/badge-72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'Ver productos',
                icon: '/img/checkmark.png'
            },
            {
                action: 'close',
                title: 'Cerrar',
                icon: '/img/xmark.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('Deportes Güemes', options)
    );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
    console.log('🔔 Notification clicked:', event.action);
    
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Message handling from main thread
self.addEventListener('message', (event) => {
    console.log('💬 Message received:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    } else if (event.data && event.data.type === 'CACHE_URLS') {
        event.waitUntil(
            cacheUrls(event.data.urls)
        );
    }
});

/**
 * Cache specific URLs on demand
 */
async function cacheUrls(urls) {
    const cache = await caches.open(DYNAMIC_CACHE);
    
    for (const url of urls) {
        try {
            await cache.add(url);
            console.log('✅ Cached URL:', url);
        } catch (error) {
            console.error('❌ Failed to cache URL:', url, error);
        }
    }
}

// Periodic background sync (if supported)
self.addEventListener('periodicsync', (event) => {
    console.log('⏰ Periodic sync triggered:', event.tag);
    
    if (event.tag === 'product-update') {
        event.waitUntil(updateProductCache());
    }
});

/**
 * Update product cache in background
 */
async function updateProductCache() {
    try {
        console.log('🔄 Updating product cache...');
        
        const response = await fetch('/JS/productos.json');
        if (response.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            await cache.put('/JS/productos.json', response);
            console.log('✅ Product cache updated');
        }
    } catch (error) {
        console.error('❌ Failed to update product cache:', error);
    }
}

console.log('🚀 Service Worker loaded successfully');