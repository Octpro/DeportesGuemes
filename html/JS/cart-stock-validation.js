/**
 * Cart Stock Validation System
 * Handles stock validation for cart quantity controls
 */

console.log('🛒 Loading cart-stock-validation.js...');

class CartStockValidator {
    constructor() {
        this.productosAgrupados = [];
        this.init();
    }

    init() {
        console.log('🔧 Initializing cart stock validator...');
        
        // Wait for products to be loaded
        this.waitForProducts();
    }

    waitForProducts() {
        const checkProducts = () => {
            if (typeof productosAgrupados !== 'undefined' && productosAgrupados.length > 0) {
                this.productosAgrupados = productosAgrupados;
                this.setupCartValidation();
                console.log('✅ Cart stock validator initialized with products');
            } else {
                setTimeout(checkProducts, 500);
            }
        };
        checkProducts();
    }

    setupCartValidation() {
        // Setup validation for any existing cart controls
        this.setupExistingCartControls();
        
        // Setup mutation observer to handle dynamically added cart controls
        this.setupMutationObserver();
    }

    setupExistingCartControls() {
        // Look for cart quantity controls
        const quantityControls = document.querySelectorAll('.cantidad-btn, .cart-quantity-btn');
        quantityControls.forEach(btn => {
            this.setupQuantityButton(btn);
        });
    }

    setupMutationObserver() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // Check for quantity buttons in added nodes
                        const quantityBtns = node.querySelectorAll ? 
                            node.querySelectorAll('.cantidad-btn, .cart-quantity-btn') : [];
                        
                        quantityBtns.forEach(btn => {
                            this.setupQuantityButton(btn);
                        });

                        // Check if the node itself is a quantity button
                        if (node.classList && (node.classList.contains('cantidad-btn') || 
                            node.classList.contains('cart-quantity-btn'))) {
                            this.setupQuantityButton(node);
                        }
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    setupQuantityButton(button) {
        if (button.dataset.stockValidationSetup) {
            return; // Already setup
        }

        button.dataset.stockValidationSetup = 'true';

        // Add click event listener with stock validation
        button.addEventListener('click', (e) => {
            this.handleQuantityChange(e);
        });
    }

    handleQuantityChange(event) {
        const button = event.target;
        const isIncrease = button.textContent.includes('+') || button.classList.contains('increase');
        const isDecrease = button.textContent.includes('-') || button.classList.contains('decrease');

        if (!isIncrease && !isDecrease) {
            return; // Not a quantity button
        }

        // Find the product ID
        const productId = this.findProductId(button);
        if (!productId) {
            console.warn('Could not find product ID for quantity button');
            return;
        }

        // Find the product data
        const producto = this.findProductById(productId);
        if (!producto) {
            console.warn('Could not find product data for ID:', productId);
            return;
        }

        // Find current quantity
        const currentQuantity = this.getCurrentQuantity(button);
        
        if (isIncrease) {
            // Validate stock before allowing increase
            if (currentQuantity >= producto.stock) {
                event.preventDefault();
                event.stopPropagation();
                this.showStockMessage(producto.titulo, producto.stock);
                return false;
            }
        }

        // Allow the operation to continue
        return true;
    }

    findProductId(button) {
        // Try different methods to find product ID
        
        // Method 1: data-product-id attribute
        if (button.dataset.productId) {
            return button.dataset.productId;
        }

        // Method 2: data-cart-id attribute
        if (button.dataset.cartId) {
            return button.dataset.cartId;
        }

        // Method 3: Look in parent elements
        let parent = button.parentElement;
        while (parent && parent !== document.body) {
            if (parent.dataset.productId) {
                return parent.dataset.productId;
            }
            if (parent.dataset.cartId) {
                return parent.dataset.cartId;
            }
            parent = parent.parentElement;
        }

        // Method 4: Look for product card container
        const productCard = button.closest('.producto, .cart-item, .carrito-producto');
        if (productCard) {
            return productCard.dataset.productId || productCard.dataset.cartId;
        }

        return null;
    }

    getCurrentQuantity(button) {
        // Find quantity input or display near the button
        const container = button.closest('.cantidad-controls, .quantity-controls');
        if (container) {
            const quantityInput = container.querySelector('input[type="number"], .cantidad-display, .quantity-display');
            if (quantityInput) {
                return parseInt(quantityInput.value || quantityInput.textContent) || 1;
            }
        }

        // Look for quantity in siblings
        const siblings = Array.from(button.parentElement.children);
        for (const sibling of siblings) {
            if (sibling.tagName === 'INPUT' && sibling.type === 'number') {
                return parseInt(sibling.value) || 1;
            }
            if (sibling.classList.contains('cantidad-display') || sibling.classList.contains('quantity-display')) {
                return parseInt(sibling.textContent) || 1;
            }
        }

        return 1;
    }

    findProductById(productId) {
        // Search in grouped products
        for (const producto of this.productosAgrupados) {
            if (producto.id === productId) {
                return producto.hasVariants ? 
                    producto.variantes[producto.selectedVariant] : producto;
            }
            
            // Check variants
            if (producto.hasVariants && producto.variantes) {
                for (const variant of producto.variantes) {
                    if (variant.id === productId) {
                        return variant;
                    }
                }
            }
        }

        // Fallback: search in original products array if available
        if (typeof productos !== 'undefined') {
            return productos.find(p => p.id === productId);
        }

        return null;
    }

    showStockMessage(productTitle, availableStock) {
        // Create and show stock limit message
        const message = document.createElement('div');
        message.className = 'stock-limit-message';
        message.innerHTML = `
            <div class="stock-message-content">
                <i class="bi bi-exclamation-triangle"></i>
                <span>Solo hay ${availableStock} unidades disponibles de "${productTitle}"</span>
            </div>
        `;

        // Add styles
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
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 500;
            animation: slideIn 0.3s ease;
            max-width: 400px;
        `;

        document.body.appendChild(message);

        // Remove after 3 seconds
        setTimeout(() => {
            message.remove();
        }, 3000);

        console.log(`⚠️ Stock limit reached for ${productTitle}: ${availableStock} units`);
    }

    // Method to validate cart quantities against current stock
    validateCartStock() {
        const cart = JSON.parse(localStorage.getItem('productos-en-carrito') || '[]');
        let hasChanges = false;
        
        const validatedCart = cart.map(item => {
            const producto = this.findProductById(item.id);
            if (producto && item.cantidad > producto.stock) {
                console.warn(`Adjusting quantity for ${item.titulo}: ${item.cantidad} -> ${producto.stock}`);
                hasChanges = true;
                return {
                    ...item,
                    cantidad: Math.max(1, producto.stock)
                };
            }
            return item;
        });

        if (hasChanges) {
            localStorage.setItem('productos-en-carrito', JSON.stringify(validatedCart));
            console.log('✅ Cart quantities validated and adjusted');
        }

        return validatedCart;
    }

    // Method to check if a quantity increase is valid
    canIncreaseQuantity(productId, currentQuantity) {
        const producto = this.findProductById(productId);
        if (!producto) {
            return false;
        }
        
        return currentQuantity < producto.stock;
    }

    // Method to get maximum allowed quantity for a product
    getMaxQuantity(productId) {
        const producto = this.findProductById(productId);
        return producto ? producto.stock : 1;
    }
}

// Initialize cart stock validator
let cartStockValidator;

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        cartStockValidator = new CartStockValidator();
    });
} else {
    cartStockValidator = new CartStockValidator();
}

// Export for use in other scripts
window.CartStockValidator = CartStockValidator;
window.cartStockValidator = cartStockValidator;

console.log('✅ cart-stock-validation.js loaded');