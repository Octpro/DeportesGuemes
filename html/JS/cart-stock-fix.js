/**
 * Cart Stock Fix - Direct implementation for cart page
 * This ensures stock validation works correctly in carrito.html
 */

console.log('🛒 Loading cart-stock-fix.js...');

// Global variables
let productosData = [];
let stockValidationEnabled = false;

// Load products data
async function loadProductsForStockValidation() {
    try {
        console.log('📦 Loading products data for stock validation...');
        const response = await fetch('JS/productos.json');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!Array.isArray(data) || data.length === 0) {
            throw new Error('Invalid products data: not an array or empty');
        }
        
        productosData = data;
        stockValidationEnabled = true;
        
        console.log('✅ Products loaded for stock validation:', productosData.length, 'products');
        
        // Log first few products for debugging
        productosData.slice(0, 3).forEach(p => {
            console.log(`📋 Product: ${p.titulo} (${p.id}) - Stock: ${p.stock}`);
        });
        
        // Also set global variables for compatibility
        window.productos = data;
        window.productosAgrupados = data;
        
        return true;
    } catch (error) {
        console.error('❌ Error loading products for stock validation:', error);
        console.error('Full error:', error);
        
        // Try to use existing global data as fallback
        if (typeof window.productos !== 'undefined' && Array.isArray(window.productos)) {
            console.log('🔄 Using existing global productos data as fallback');
            productosData = window.productos;
            stockValidationEnabled = true;
            return true;
        }
        
        return false;
    }
}

// Find product by ID with detailed logging
function findProductForStockValidation(productId) {
    console.log('🔍 Looking for product:', productId);
    console.log('📊 Stock validation enabled:', stockValidationEnabled);
    console.log('📦 Products data length:', productosData.length);
    
    if (!stockValidationEnabled) {
        console.warn('⚠️ Stock validation not enabled');
        return null;
    }
    
    if (!productosData.length) {
        console.warn('⚠️ No products data available');
        return null;
    }
    
    const product = productosData.find(p => p.id === productId);
    
    if (product) {
        console.log('✅ Product found:', product.titulo, 'Stock:', product.stock);
    } else {
        console.warn('❌ Product not found:', productId);
        console.log('📋 Available products:', productosData.map(p => `${p.id} (${p.titulo})`).join(', '));
    }
    
    return product;
}

// Show stock limit message
function showStockLimitMessage(productTitle, availableStock) {
    console.log('🚫 Showing stock limit message:', productTitle, availableStock);
    
    // Remove any existing messages
    const existingMessages = document.querySelectorAll('.stock-limit-message');
    existingMessages.forEach(msg => msg.remove());
    
    const message = document.createElement('div');
    message.className = 'stock-limit-message';
    message.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="bi bi-exclamation-triangle" style="font-size: 1.2em;"></i>
            <span>Solo hay ${availableStock} unidades disponibles de "${productTitle}"</span>
        </div>
    `;

    message.style.cssText = `
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
        animation: slideInFromRight 0.3s ease;
        max-width: 400px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `;

    // Add animation styles
    if (!document.querySelector('#stock-message-animation')) {
        const style = document.createElement('style');
        style.id = 'stock-message-animation';
        style.textContent = `
            @keyframes slideInFromRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }

    document.body.appendChild(message);

    // Remove after 4 seconds
    setTimeout(() => {
        if (message.parentNode) {
            message.remove();
        }
    }, 4000);
}

// Validate stock increase
function validateStockIncrease(productId, currentQuantity) {
    if (!stockValidationEnabled) {
        console.warn('⚠️ Stock validation disabled, allowing increase');
        return true;
    }
    
    const product = findProductForStockValidation(productId);
    if (!product) {
        console.warn('⚠️ Product not found, allowing increase (fallback behavior)');
        return true; // Changed to true to allow increase when product data is not found
    }
    
    const newQuantity = currentQuantity + 1;
    console.log(`📊 Stock check: ${newQuantity} vs ${product.stock}`);
    
    if (newQuantity > product.stock) {
        console.log('🚫 Stock limit would be exceeded');
        showStockLimitMessage(product.titulo, product.stock);
        return false;
    }
    
    console.log('✅ Stock validation passed');
    return true;
}

// Override the global updateQuantity function
function overrideUpdateQuantity() {
    // Store original function if it exists
    if (typeof window.originalUpdateQuantity === 'undefined' && typeof updateQuantity === 'function') {
        window.originalUpdateQuantity = updateQuantity;
        console.log('💾 Original updateQuantity function stored');
    }
    
    // Define new updateQuantity with stock validation
    window.updateQuantity = function(cartId, change) {
        console.log('🔄 Stock-validated updateQuantity called:', cartId, change);
        
        try {
            let productosEnCarrito = JSON.parse(localStorage.getItem("productos-en-carrito") || "[]");
            const item = productosEnCarrito.find(p => (p.cartId || p.id) === cartId);
            
            if (!item) {
                console.warn('❌ Item not found in cart:', cartId);
                return;
            }
            
            const currentQuantity = item.cantidad || 1;
            const newQuantity = currentQuantity + change;
            
            console.log('📊 Quantity change:', currentQuantity, '->', newQuantity);
            
            if (newQuantity <= 0) {
                console.log('🗑️ Removing item (quantity <= 0)');
                if (typeof removeFromCart === 'function') {
                    removeFromCart(cartId);
                } else {
                    // Fallback removal
                    productosEnCarrito = productosEnCarrito.filter(p => (p.cartId || p.id) !== cartId);
                    localStorage.setItem("productos-en-carrito", JSON.stringify(productosEnCarrito));
                    if (typeof displayCartItems === 'function') {
                        displayCartItems(productosEnCarrito);
                    }
                }
                return;
            }
            
            // Validate stock if increasing quantity
            if (change > 0) {
                console.log('📈 Validating stock increase...');
                if (!validateStockIncrease(cartId, currentQuantity)) {
                    console.log('🚫 Stock validation failed, blocking increase');
                    return;
                }
            }
            
            // Update quantity
            item.cantidad = newQuantity;
            localStorage.setItem("productos-en-carrito", JSON.stringify(productosEnCarrito));
            
            console.log('💾 Cart updated successfully');
            
            // Refresh display
            if (typeof displayCartItems === 'function') {
                displayCartItems(productosEnCarrito);
            }
            
        } catch (error) {
            console.error('❌ Error in stock-validated updateQuantity:', error);
        }
    };
    
    console.log('✅ updateQuantity function overridden with stock validation');
}

// Initialize stock validation
async function initializeStockValidation() {
    console.log('🚀 Initializing stock validation for cart...');
    
    // Load products data
    const loaded = await loadProductsForStockValidation();
    
    if (loaded) {
        // Override updateQuantity function
        overrideUpdateQuantity();
        
        console.log('✅ Stock validation initialized successfully');
        
        // Test the system
        setTimeout(() => {
            console.log('🧪 Testing stock validation system...');
            const testProduct = findProductForStockValidation('cam001');
            if (testProduct) {
                console.log('✅ Stock validation test passed');
            } else {
                console.warn('⚠️ Stock validation test failed');
            }
        }, 1000);
    } else {
        console.error('❌ Failed to initialize stock validation');
    }
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeStockValidation);
} else {
    initializeStockValidation();
}

// Also initialize after a delay to ensure other scripts have loaded
setTimeout(initializeStockValidation, 2000);

console.log('✅ cart-stock-fix.js loaded');