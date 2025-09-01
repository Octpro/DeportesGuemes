// Fixed cart functionality
console.log('🛒 Loading carrito-fixed.js...');

// Initialize cart page
function initializeCart() {
    console.log('🔧 Initializing cart page...');
    
    // Setup menu buttons
    setupMenuButtons();
    
    // Setup back buttons
    setupBackButtons();
    
    // Load and display cart
    loadAndDisplayCart();
    
    console.log('✅ Cart page initialized');
}

// Setup menu buttons (same as main page)
function setupMenuButtons() {
    const openMenu = document.getElementById('open-menu');
    const closeMenu = document.getElementById('close-menu');
    const aside = document.querySelector('aside');
    
    // Open menu
    if (openMenu && aside) {
        openMenu.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Open menu clicked');
            aside.classList.add('aside-visible');
        });
    }
    
    // Close menu
    if (closeMenu && aside) {
        closeMenu.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Close menu clicked');
            aside.classList.remove('aside-visible');
        });
    }
    
    console.log('✅ Menu buttons configured');
}

// Setup back buttons
function setupBackButtons() {
    console.log('🔧 Setting up back buttons...');
    
    // All "Seguir comprando" buttons
    const backButtons = document.querySelectorAll('a[href="index.html"]');
    backButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            console.log('Back button clicked');
            // Let the default behavior happen (navigate to index.html)
        });
    });
    
    // Specific back button in sidebar
    const sidebarBackBtn = document.querySelector('.boton-volver');
    if (sidebarBackBtn) {
        sidebarBackBtn.addEventListener('click', function(e) {
            console.log('Sidebar back button clicked');
            // Close mobile menu before navigating
            const aside = document.querySelector('aside');
            if (aside) {
                aside.classList.remove('aside-visible');
            }
        });
    }
    
    console.log('✅ Back buttons configured');
}

// Load and display cart items
function loadAndDisplayCart() {
    console.log('📦 Loading cart items...');
    
    try {
        const cartData = localStorage.getItem("productos-en-carrito");
        let productosEnCarrito = [];
        
        if (cartData) {
            productosEnCarrito = JSON.parse(cartData);
        }
        
        console.log('Cart items loaded:', productosEnCarrito.length);
        
        // Update cart display
        displayCartItems(productosEnCarrito);
        
    } catch (error) {
        console.error('❌ Error loading cart:', error);
        displayCartItems([]);
    }
}

// Display cart items
function displayCartItems(items) {
    const cartContainer = document.getElementById('carrito-productos');
    const emptyCart = document.getElementById('carrito-vacio');
    const cartSummary = document.getElementById('carrito-resumen');
    const cartItemCount = document.getElementById('cart-item-count');
    
    if (items.length === 0) {
        // Show empty cart
        if (emptyCart) {
            emptyCart.style.display = 'block';
            emptyCart.classList.remove('disabled');
        }
        if (cartContainer) {
            cartContainer.style.display = 'none';
            cartContainer.classList.add('disabled');
        }
        if (cartSummary) {
            cartSummary.classList.add('disabled');
        }
        if (cartItemCount) {
            cartItemCount.textContent = '0';
        }
    } else {
        // Show cart items
        if (emptyCart) {
            emptyCart.style.display = 'none';
            emptyCart.classList.add('disabled');
        }
        if (cartContainer) {
            cartContainer.style.display = 'block';
            cartContainer.classList.remove('disabled');
        }
        if (cartSummary) {
            cartSummary.classList.remove('disabled');
        }
        if (cartItemCount) {
            cartItemCount.textContent = items.length;
        }
        
        // Render items
        if (cartContainer) {
            cartContainer.innerHTML = items.map(item => `
                <div class="carrito-producto" data-cart-id="${item.cartId || item.id}">
                    <img class="carrito-producto-imagen" src="${item.imagen}" alt="${item.titulo}">
                    <div class="carrito-producto-info">
                        <div class="carrito-producto-titulo">
                            <h3>${item.titulo}</h3>
                            ${item.talle && item.talle !== 'Único' ? `<p class="producto-talle">Talle: ${item.talle}</p>` : ''}
                        </div>
                        <div class="carrito-producto-controles">
                            <div class="cantidad-controles">
                                <button class="cantidad-btn cantidad-menos" data-cart-id="${item.cartId || item.id}">-</button>
                                <span class="cantidad-display">${item.cantidad}</span>
                                <button class="cantidad-btn cantidad-mas" data-cart-id="${item.cartId || item.id}">+</button>
                            </div>
                            <div class="carrito-producto-precio">
                                <span class="precio-unitario">$${item.precio} c/u</span>
                                <span class="precio-subtotal">$${(parseFloat(item.precio) * item.cantidad).toFixed(0)}</span>
                            </div>
                        </div>
                    </div>
                    <button class="carrito-producto-eliminar" data-cart-id="${item.cartId || item.id}" title="Eliminar producto">
                        <i class="bi bi-trash-fill"></i>
                    </button>
                </div>
            `).join('');
            
            // Setup cart controls
            setupCartControls();
        }
        
        // Update summary
        updateCartSummary(items);
    }
}

// Update cart summary
function updateCartSummary(items) {
    const resumenCantidad = document.getElementById('resumen-cantidad');
    const resumenSubtotal = document.getElementById('resumen-subtotal');
    const total = document.getElementById('total');
    
    const totalItems = items.reduce((sum, item) => sum + item.cantidad, 0);
    const totalPrice = items.reduce((sum, item) => sum + (parseFloat(item.precio) * item.cantidad), 0);
    
    if (resumenCantidad) resumenCantidad.textContent = totalItems;
    if (resumenSubtotal) resumenSubtotal.textContent = `$${totalPrice.toFixed(0)}`;
    if (total) total.textContent = `$${totalPrice.toFixed(0)}`;
}

// Setup cart controls
function setupCartControls() {
    // Quantity controls
    const menosButtons = document.querySelectorAll('.cantidad-menos');
    const masButtons = document.querySelectorAll('.cantidad-mas');
    const removeButtons = document.querySelectorAll('.carrito-producto-eliminar');
    const vaciarButton = document.getElementById('carrito-acciones-vaciar');
    const comprarButton = document.getElementById('carrito-acciones-comprar');
    
    // Decrease quantity
    menosButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const cartId = e.target.dataset.cartId;
            updateQuantity(cartId, -1);
        });
    });
    
    // Increase quantity
    masButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const cartId = e.target.dataset.cartId;
            updateQuantity(cartId, 1);
        });
    });
    
    // Remove items
    removeButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const cartId = e.target.dataset.cartId;
            removeFromCart(cartId);
        });
    });
    
    // Clear cart
    if (vaciarButton) {
        vaciarButton.addEventListener('click', clearCart);
    }
    
    // WhatsApp checkout
    if (comprarButton) {
        comprarButton.addEventListener('click', sendWhatsAppMessage);
    }
}

// Update item quantity
function updateQuantity(cartId, change) {
    try {
        let productosEnCarrito = JSON.parse(localStorage.getItem("productos-en-carrito") || "[]");
        const item = productosEnCarrito.find(p => (p.cartId || p.id) === cartId);
        
        if (item) {
            const newQuantity = item.cantidad + change;
            if (newQuantity <= 0) {
                removeFromCart(cartId);
                return;
            }
            
            item.cantidad = newQuantity;
            localStorage.setItem("productos-en-carrito", JSON.stringify(productosEnCarrito));
            
            // Refresh display
            displayCartItems(productosEnCarrito);
        }
    } catch (error) {
        console.error('❌ Error updating quantity:', error);
    }
}

// Remove item from cart
function removeFromCart(cartId) {
    try {
        let productosEnCarrito = JSON.parse(localStorage.getItem("productos-en-carrito") || "[]");
        productosEnCarrito = productosEnCarrito.filter(item => (item.cartId || item.id) !== cartId);
        localStorage.setItem("productos-en-carrito", JSON.stringify(productosEnCarrito));
        
        // Refresh display
        displayCartItems(productosEnCarrito);
        
        console.log('Product removed from cart');
    } catch (error) {
        console.error('❌ Error removing from cart:', error);
    }
}

// Clear entire cart
function clearCart() {
    if (confirm('¿Estás seguro de que quieres vaciar el carrito?')) {
        localStorage.removeItem("productos-en-carrito");
        displayCartItems([]);
        console.log('Cart cleared');
    }
}

// Send WhatsApp message
function sendWhatsAppMessage() {
    try {
        const productosEnCarrito = JSON.parse(localStorage.getItem("productos-en-carrito") || "[]");
        
        if (productosEnCarrito.length === 0) {
            alert('Tu carrito está vacío');
            return;
        }
        
        // Create message
        let message = "¡Hola! Me interesa consultar por estos productos:\n\n";
        let total = 0;
        
        productosEnCarrito.forEach((item, index) => {
            const subtotal = parseFloat(item.precio) * item.cantidad;
            total += subtotal;
            
            message += `${index + 1}. ${item.titulo}\n`;
            if (item.talle && item.talle !== 'Único') {
                message += `   Talle: ${item.talle}\n`;
            }
            message += `   Cantidad: ${item.cantidad}\n`;
            message += `   Precio: $${item.precio} c/u\n`;
            message += `   Subtotal: $${subtotal.toFixed(0)}\n\n`;
        });
        
        message += `Total: $${total.toFixed(0)}\n\n`;
        message += "¿Podrían confirmarme disponibilidad y forma de pago?";
        
        // WhatsApp number (replace with actual number)
        const phoneNumber = "5491234567890"; // Replace with actual WhatsApp number
        const whatsappUrl = `https://wa.me/${phoneNumber}?text=${encodeURIComponent(message)}`;
        
        window.open(whatsappUrl, '_blank');
        
    } catch (error) {
        console.error('❌ Error sending WhatsApp message:', error);
        alert('Error al generar el mensaje de WhatsApp');
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeCart);
} else {
    initializeCart();
}

console.log('✅ carrito-fixed.js loaded');