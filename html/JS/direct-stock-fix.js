/**
 * Direct Stock Fix - Immediate and simple solution
 * This directly patches the cart functionality with stock validation
 */

console.log('🛒 Loading direct-stock-fix.js...');

// Stock data storage
let stockLookup = {};

// Load stock data immediately
(async function loadStockData() {
    try {
        console.log('📦 LOADING STOCK DATA...');
        const response = await fetch('JS/productos.json');

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const products = await response.json();
        console.log('📋 Raw products data:', products.length, 'items');

        if (!Array.isArray(products) || products.length === 0) {
            throw new Error('Invalid products data');
        }

        // Build lookup table with detailed logging
        products.forEach(p => {
            if (p.id && p.titulo && typeof p.stock === 'number') {
                stockLookup[p.id] = {
                    titulo: p.titulo,
                    stock: p.stock
                };
                console.log(`📋 Loaded: ${p.titulo} (${p.id}) - Stock: ${p.stock}`);
            } else {
                console.warn('⚠️ Invalid product data:', p);
            }
        });

        console.log('✅ STOCK DATA LOADED:', Object.keys(stockLookup).length, 'products');
        console.log('🔍 Stock lookup table:', stockLookup);

        // Verify specific product
        if (stockLookup['cam001']) {
            console.log('✅ cam001 found:', stockLookup['cam001']);
        } else {
            console.error('❌ cam001 NOT FOUND in stock data');
        }

    } catch (error) {
        console.error('❌ CRITICAL: Failed to load stock data:', error);
        console.error('Full error:', error);
    }
})();

// Stock validation function with variant support
function validateStock(productId, requestedQuantity) {
    console.log('🔍 validateStock called with:', productId, requestedQuantity);
    console.log('📦 Available stock data:', Object.keys(stockLookup));

    let stockInfo = stockLookup[productId];

    // If not found, try to find variant or base product
    if (!stockInfo) {
        console.log('🔍 Product not found directly, trying variants...');
        
        // Try different patterns for variant IDs
        const possibleIds = [
            productId.replace(/_[A-Z]+$/, ''), // Remove size suffix: cam004_azul_M -> cam004_azul
            productId.split('_')[0], // Get base: cam004_azul_M -> cam004
            productId.replace(/_[A-Z]+$/, '').split('_')[0] // Base without size: cam004_azul_M -> cam004
        ];
        
        for (const tryId of possibleIds) {
            console.log('🔍 Trying ID:', tryId);
            if (stockLookup[tryId]) {
                console.log(`✅ Found product: ${tryId} for original: ${productId}`);
                stockInfo = stockLookup[tryId];
                break;
            }
        }
    }

    if (!stockInfo) {
        console.error('❌ CRITICAL: No stock info found for:', productId);
        const triedIds = [
            productId.replace(/_[A-Z]+$/, ''),
            productId.split('_')[0],
            productId.replace(/_[A-Z]+$/, '').split('_')[0]
        ];
        console.log('🔍 Tried IDs:', triedIds);
        console.log('🚫 ALLOWING operation as fallback (cannot validate)');
        return true; // Allow if we can't find stock data (fallback)
    }

    console.log(`📊 VALIDATION: ${requestedQuantity} requested vs ${stockInfo.stock} available for ${stockInfo.titulo}`);

    if (requestedQuantity > stockInfo.stock) {
        console.error('🚫 STOCK LIMIT EXCEEDED:', requestedQuantity, '>', stockInfo.stock);
        showStockAlert(stockInfo.titulo, stockInfo.stock);
        return false;
    }

    console.log('✅ VALIDATION PASSED');
    return true;
}

// Show stock alert
function showStockAlert(productTitle, maxStock) {
    // Remove existing alerts
    document.querySelectorAll('.direct-stock-alert').forEach(el => el.remove());

    const alert = document.createElement('div');
    alert.className = 'direct-stock-alert';
    alert.innerHTML = `
        <i class="bi bi-exclamation-triangle"></i>
        Solo hay ${maxStock} unidades disponibles de "${productTitle}"
    `;

    alert.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #ff6b35;
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 1001;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 10px;
        animation: slideInFromRight 0.3s ease;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `;

    // Add animation
    if (!document.querySelector('#direct-stock-animation')) {
        const style = document.createElement('style');
        style.id = 'direct-stock-animation';
        style.textContent = `
            @keyframes slideInFromRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }

    document.body.appendChild(alert);

    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 3000);
}

// Direct patch for updateQuantity
function patchUpdateQuantity() {
    console.log('🔧 Patching updateQuantity function...');

    // Store original if it exists
    const originalUpdateQuantity = window.updateQuantity;

    // Create patched version
    window.updateQuantity = function (cartId, change) {
        console.log('🔄 PATCHED updateQuantity called:', cartId, change);
        console.log('📊 Stock lookup available:', Object.keys(stockLookup).length > 0);

        try {
            // Get current cart state
            const cart = JSON.parse(localStorage.getItem("productos-en-carrito") || "[]");
            const item = cart.find(p => (p.cartId || p.id) === cartId);

            if (!item) {
                console.warn('❌ Item not found:', cartId);
                return;
            }

            const currentQuantity = item.cantidad || 1;
            const newQuantity = currentQuantity + change;

            console.log(`📊 Quantity: ${currentQuantity} -> ${newQuantity}`);

            // Handle removal
            if (newQuantity <= 0) {
                console.log('🗑️ Removing item');
                if (typeof removeFromCart === 'function') {
                    removeFromCart(cartId);
                } else {
                    // Fallback removal
                    const updatedCart = cart.filter(p => (p.cartId || p.id) !== cartId);
                    localStorage.setItem("productos-en-carrito", JSON.stringify(updatedCart));
                    if (typeof displayCartItems === 'function') {
                        displayCartItems(updatedCart);
                    }
                }
                return;
            }

            // Validate stock for increases
            if (change > 0) {
                console.log('📈 INCREASE DETECTED - Running stock validation...');
                const validationResult = validateStock(cartId, newQuantity);
                console.log('🔍 Validation result:', validationResult);

                if (!validationResult) {
                    console.error('🚫 STOCK VALIDATION FAILED - BLOCKING OPERATION');
                    return; // Block the operation
                }

                console.log('✅ Stock validation passed, proceeding...');
            }

            // Update quantity
            item.cantidad = newQuantity;
            localStorage.setItem("productos-en-carrito", JSON.stringify(cart));

            // Refresh display
            if (typeof displayCartItems === 'function') {
                displayCartItems(cart);
            }

            console.log('✅ Quantity updated successfully');

        } catch (error) {
            console.error('❌ Error in patched updateQuantity:', error);

            // Fallback to original if available
            if (originalUpdateQuantity) {
                originalUpdateQuantity(cartId, change);
            }
        }
    };

    console.log('✅ updateQuantity patched successfully');
}

// Initialize immediately and with delays
patchUpdateQuantity();

// Re-patch after delays to ensure it sticks
setTimeout(patchUpdateQuantity, 500);
setTimeout(patchUpdateQuantity, 1000);
setTimeout(patchUpdateQuantity, 2000);

// Also patch when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', patchUpdateQuantity);
} else {
    setTimeout(patchUpdateQuantity, 100);
}

// Debug function - call this in console to check status
window.debugStockValidation = function () {
    console.log('🔍 STOCK VALIDATION DEBUG:');
    console.log('📦 Stock data loaded:', Object.keys(stockLookup).length, 'products');
    console.log('📋 Stock lookup:', stockLookup);
    console.log('🔧 updateQuantity function:', typeof window.updateQuantity);

    // Test validation
    if (stockLookup['cam001']) {
        console.log('✅ Testing cam001 validation:');
        console.log('  - Stock:', stockLookup['cam001'].stock);
        console.log('  - Test 26 units:', validateStock('cam001', 26));
        console.log('  - Test 25 units:', validateStock('cam001', 25));
    }

    return {
        stockDataLoaded: Object.keys(stockLookup).length > 0,
        stockLookup: stockLookup,
        updateQuantityPatched: typeof window.updateQuantity === 'function'
    };
};

console.log('✅ direct-stock-fix.js loaded');
console.log('🔧 Call debugStockValidation() in console to check status');