/**
 * Cart UI Manager
 * Handles cart display and user interactions with stock validation
 */

console.log('🛒 Loading cart-ui-manager.js...');

class CartUIManager {
    constructor() {
        this.cartManager = null;
        this.cartContainer = null;
        this.init();
    }

    init() {
        console.log('🔧 Initializing cart UI manager...');
        
        // Wait for cart manager to be available
        this.waitForCartManager();
    }

    waitForCartManager() {
        const checkCartManager = () => {
            if (typeof CartDataManager !== 'undefined') {
                this.cartManager = new CartDataManager();
                this.setupCartUI();
                console.log('✅ Cart UI manager initialized');
            } else {
                setTimeout(checkCartManager, 500);
            }
        };
        checkCartManager();
    }

    setupCartUI() {
        // Look for cart containers
        this.findCartContainers();
        
        // Setup mutation observer for dynamic cart content
        this.setupMutationObserver();
        
        // Setup existing cart controls
        this.setupExistingControls();
    }

    findCartContainers() {
        // Common cart container selectors
        const selectors = [
            '#carrito-productos',
            '.cart-items',
            '.carrito-contenido',
            '.cart-container'
        ];

        for (const selector of selectors) {
            const container = document.querySelector(selector);
            if (container) {
                this.cartContainer = container;
                console.log('✅ Found cart container:', selector);
                break;
            }
        }
    }

    setupMutationObserver() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        this.setupCartControlsInNode(node);
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    setupExistingControls() {
        // Setup controls in the entire document
        this.setupCartControlsInNode(document.body);
    }

    setupCartControlsInNode(node) {
        // Find quantity increase buttons
        const increaseButtons = node.querySelectorAll ? 
            node.querySelectorAll('.cantidad-mas, .cart-increase, [data-action="increase"]') : [];
        
        increaseButtons.forEach(btn => {
            if (!btn.dataset.cartUISetup) {
                btn.dataset.cartUISetup = 'true';
                btn.addEventListener('click', (e) => this.handleQuantityIncrease(e));
            }
        });

        // Find quantity decrease buttons
        const decreaseButtons = node.querySelectorAll ? 
            node.querySelectorAll('.cantidad-menos, .cart-decrease, [data-action="decrease"]') : [];
        
        decreaseButtons.forEach(btn => {
            if (!btn.dataset.cartUISetup) {
                btn.dataset.cartUISetup = 'true';
                btn.addEventListener('click', (e) => this.handleQuantityDecrease(e));
            }
        });

        // Find quantity inputs
        const quantityInputs = node.querySelectorAll ? 
            node.querySelectorAll('.cantidad-input, .cart-quantity-input, input[type="number"][data-product-id]') : [];
        
        quantityInputs.forEach(input => {
            if (!input.dataset.cartUISetup) {
                input.dataset.cartUISetup = 'true';
                input.addEventListener('change', (e) => this.handleQuantityInputChange(e));
                input.addEventListener('blur', (e) => this.handleQuantityInputChange(e));
            }
        });

        // Check if the node itself is a control
        if (node.classList) {
            if (node.classList.contains('cantidad-mas') || node.classList.contains('cart-increase')) {
                if (!node.dataset.cartUISetup) {
                    node.dataset.cartUISetup = 'true';
                    node.addEventListener('click', (e) => this.handleQuantityIncrease(e));
                }
            }
            
            if (node.classList.contains('cantidad-menos') || node.classList.contains('cart-decrease')) {
                if (!node.dataset.cartUISetup) {
                    node.dataset.cartUISetup = 'true';
                    node.addEventListener('click', (e) => this.handleQuantityDecrease(e));
                }
            }
        }
    }

    handleQuantityIncrease(event) {
        event.preventDefault();
        event.stopPropagation();

        const button = event.target;
        const productId = this.getProductIdFromElement(button);
        
        if (!productId) {
            console.warn('Could not find product ID for quantity increase');
            return;
        }

        console.log('🔼 Increasing quantity for product:', productId);

        // Use cart manager to increase quantity with stock validation
        const success = this.cartManager.increaseQuantity(productId);
        
        if (success) {
            // Update UI
            this.updateQuantityDisplay(button, productId);
            this.updateCartSummary();
            
            // Trigger custom event
            this.dispatchCartUpdateEvent('quantity-increased', productId);
        }
    }

    handleQuantityDecrease(event) {
        event.preventDefault();
        event.stopPropagation();

        const button = event.target;
        const productId = this.getProductIdFromElement(button);
        
        if (!productId) {
            console.warn('Could not find product ID for quantity decrease');
            return;
        }

        console.log('🔽 Decreasing quantity for product:', productId);

        // Use cart manager to decrease quantity
        const success = this.cartManager.decreaseQuantity(productId);
        
        if (success) {
            // Update UI
            this.updateQuantityDisplay(button, productId);
            this.updateCartSummary();
            
            // Trigger custom event
            this.dispatchCartUpdateEvent('quantity-decreased', productId);
        }
    }

    handleQuantityInputChange(event) {
        const input = event.target;
        const productId = this.getProductIdFromElement(input);
        const newQuantity = parseInt(input.value) || 1;
        
        if (!productId) {
            console.warn('Could not find product ID for quantity input change');
            return;
        }

        console.log('📝 Changing quantity via input for product:', productId, 'to:', newQuantity);

        // Validate against stock
        const producto = this.cartManager.findProductById(productId);
        if (producto && newQuantity > producto.stock) {
            // Reset to maximum available stock
            input.value = producto.stock;
            this.cartManager.showStockMessage(producto.titulo, producto.stock);
            
            // Update cart with corrected quantity
            this.cartManager.updateQuantity(productId, producto.stock);
        } else {
            // Update cart with new quantity
            this.cartManager.updateQuantity(productId, newQuantity);
        }

        this.updateCartSummary();
        this.dispatchCartUpdateEvent('quantity-changed', productId);
    }

    getProductIdFromElement(element) {
        // Try different methods to find product ID
        
        // Method 1: Direct data attributes
        if (element.dataset.productId) {
            return element.dataset.productId;
        }
        if (element.dataset.cartId) {
            return element.dataset.cartId;
        }

        // Method 2: Look in parent elements
        let parent = element.parentElement;
        while (parent && parent !== document.body) {
            if (parent.dataset.productId) {
                return parent.dataset.productId;
            }
            if (parent.dataset.cartId) {
                return parent.dataset.cartId;
            }
            parent = parent.parentElement;
        }

        // Method 3: Look for cart item container
        const cartItem = element.closest('.carrito-producto, .cart-item, .producto');
        if (cartItem) {
            return cartItem.dataset.productId || cartItem.dataset.cartId;
        }

        return null;
    }

    updateQuantityDisplay(triggerElement, productId) {
        // Find quantity display elements for this product
        const productContainer = triggerElement.closest('.carrito-producto, .cart-item, .producto');
        if (!productContainer) return;

        const cart = this.cartManager.loadCart();
        const item = cart.find(p => p.id === productId);
        if (!item) return;

        // Update quantity displays
        const quantityDisplays = productContainer.querySelectorAll('.cantidad-display, .quantity-display');
        quantityDisplays.forEach(display => {
            display.textContent = item.cantidad;
        });

        // Update quantity inputs
        const quantityInputs = productContainer.querySelectorAll('input[type="number"]');
        quantityInputs.forEach(input => {
            input.value = item.cantidad;
        });

        // Update subtotal if present
        const subtotalElements = productContainer.querySelectorAll('.precio-subtotal, .subtotal');
        subtotalElements.forEach(subtotal => {
            const precio = parseFloat(item.precio) || 0;
            const total = precio * item.cantidad;
            subtotal.textContent = total.toFixed(0);
        });
    }

    updateCartSummary() {
        const summary = this.cartManager.getCartSummary();
        
        // Update cart count in navigation
        const cartCounts = document.querySelectorAll('#numerito, .cart-count, .cart-item-count');
        cartCounts.forEach(count => {
            count.textContent = summary.totalItems;
        });

        // Update summary elements
        const summaryElements = {
            '.resumen-cantidad, .summary-quantity': summary.totalItems,
            '.resumen-subtotal, .summary-subtotal': summary.subtotal.toFixed(0),
            '#total, .total-amount': summary.subtotal.toFixed(0)
        };

        Object.entries(summaryElements).forEach(([selector, value]) => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                element.textContent = value;
            });
        });
    }

    dispatchCartUpdateEvent(action, productId) {
        const event = new CustomEvent('cartUpdated', {
            detail: {
                action: action,
                productId: productId,
                cart: this.cartManager.loadCart(),
                summary: this.cartManager.getCartSummary()
            }
        });
        
        document.dispatchEvent(event);
    }

    // Public method to refresh cart display
    refreshCartDisplay() {
        this.updateCartSummary();
        
        // Validate stock for all items
        this.cartManager.validateCartStock();
        
        console.log('🔄 Cart display refreshed');
    }

    // Public method to validate all cart quantities
    validateAllQuantities() {
        return this.cartManager.validateCartStock();
    }
}

// Initialize cart UI manager
let cartUIManager;

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        cartUIManager = new CartUIManager();
    });
} else {
    cartUIManager = new CartUIManager();
}

// Export for use in other scripts
window.CartUIManager = CartUIManager;
window.cartUIManager = cartUIManager;

console.log('✅ cart-ui-manager.js loaded');