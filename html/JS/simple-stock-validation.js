/**
 * Simple Stock Validation - Direct and reliable
 * This replaces the complex validation with a simple, working solution
 */

console.log('🛒 Loading simple-stock-validation.js...');

// Simple global variables
let stockData = {};
let validationReady = false;

// Load stock data immediately
async function initStockValidation() {
    try {
        console.log('📦 Loading stock data...');
        const response = await fetch('JS/productos.json');
        const products = await response.json();
        
        // Create simple stock lookup
        products.forEach(product => {
            stockData[product.id] = {
                titulo: product.titulo,
                stock: product.stock
            };
        });
        
        validationReady = true;
        console.log('✅ Stock validation ready with', Object.keys(stockData).length, 'products');
        
        // Log some examples
        Object.keys(stockData).slice(0, 3).forEach(id => {
            const item = stockData[id];
            console.log(`📋 ${item.titulo} (${id}): ${item.stock} units`);
        });
        
    } catch (error) {
        console.error('❌ Failed to load stock data:', error);
        validationReady = false;
    }
}

// Simple stock check
function checkStock(productId, requestedQuantity) {
    if (!validationReady) {
        console.warn('⚠️ Stock validation not ready, allowing operation');
        return true;
    }
    
    const item = stockData[productId];
    if (!item) {
        console.warn('⚠️ Product not found in stock data:', productId);
        return true; // Allow if we can't find the product
    }
    
    console.log(`📊 Stock check: ${requestedQuantity} requested vs ${item.stock} available for ${item.titulo}`);
    
    if (requestedQuantity > item.stock) {
        console.log('🚫 Stock limit exceeded');
        showSimpleStockMessage(item.titulo, item.stock);
        return false;
    }
    
    console.log('✅ Stock check passed');
    return true;
}

// Simple stock message
function showSimpleStockMessage(productTitle, availableStock) {
    // Remove existing messages
    document.querySelectorAll('.simple-stock-message').forEach(msg => msg.remove());
    
    const message = document.createElement('div');
    message.className = 'simple-stock-message';
    message.innerHTML = `
        <i class="bi bi-exclamation-triangle"></i>
        Solo hay ${availableStock} unidades disponibles de "${productTitle}"
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
        display: flex;
        align-items: center;
        gap: 10px;
        animation: slideInRight 0.3s ease;
    `;
    
    // Add animation if not exists
    if (!document.querySelector('#simple-stock-animation')) {
        const style = document.createElement('style');
        style.id = 'simple-stock-animation';
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(message);
    
    setTimeout(() => {
        if (message.parentNode) {
            message.remove();
        }
    }, 3000);
}

// Override updateQuantity with simple validation
function setupSimpleStockValidation() {
    console.log('🔧 Setting up simple stock validation...');
    
    // Define the validated updateQuantity function immediately
    function validatedUpdateQuantity(cartId, change) {
        console.log('🔄 Validated updateQuantity called:', cartId, change);
        
        try {
            // Get current cart
            const cart = JSON.parse(localStorage.getItem("productos-en-carrito") || "[]");
            const item = cart.find(p => (p.cartId || p.id) === cartId);
            
            if (!item) {
                console.warn('❌ Item not found in cart:', cartId);
                return;
            }
            
            const currentQuantity = item.cantidad || 1;
            const newQuantity = currentQuantity + change;
            
            console.log(`📊 Quantity change: ${currentQuantity} -> ${newQuantity}`);
            
            if (newQuantity <= 0) {
                console.log('🗑️ Quantity would be <= 0, removing item');
                // Remove item logic here if needed
                return;
            }
            
            // If increasing, check stock
            if (change > 0) {
                if (!checkStock(cartId, newQuantity)) {
                    console.log('🚫 Stock validation failed, blocking increase');
                    return;
                }
            }
            
            // Update the cart
            item.cantidad = newQuantity;
            localStorage.setItem("productos-en-carrito", JSON.stringify(cart));
            
            // Refresh display if function exists
            if (typeof displayCartItems === 'function') {
                displayCartItems(cart);
            }
            
            console.log('✅ Quantity updated successfully');
            
        } catch (error) {
            console.error('❌ Error in validated updateQuantity:', error);
        }
    }
    
    // Set it immediately
    window.updateQuantity = validatedUpdateQuantity;
    console.log('✅ Simple stock validation installed immediately');
    
    // Also try to override after delays to catch late definitions
    setTimeout(() => {
        window.updateQuantity = validatedUpdateQuantity;
        console.log('🔄 Re-installed stock validation after 1s');
    }, 1000);
    
    setTimeout(() => {
        window.updateQuantity = validatedUpdateQuantity;
        console.log('🔄 Re-installed stock validation after 2s');
    }, 2000);
}

// Initialize everything
async function initializeSimpleValidation() {
    console.log('🚀 Initializing simple stock validation...');
    
    await initStockValidation();
    setupSimpleStockValidation();
    
    console.log('✅ Simple stock validation initialized');
}

// Start initialization
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeSimpleValidation);
} else {
    initializeSimpleValidation();
}

// Also try after a delay to ensure other scripts are loaded
setTimeout(initializeSimpleValidation, 1000);

console.log('✅ simple-stock-validation.js loaded');