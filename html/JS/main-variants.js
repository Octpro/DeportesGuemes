// Simplified and robust main.js with variant support
console.log('🚀 Loading main-variants.js...');

// Global variables
let productos = [];
let productosEnCarrito = [];

// DOM elements
const contenedorProductos = document.querySelector("#contenedor-productos");
const botonesCategoria = document.querySelectorAll(".boton-categoria");
const tituloPrincipal = document.querySelector(".titulo-principal");
const numerito = document.querySelector("#numerito");

// Initialize everything when DOM is ready
function initializeApp() {
    console.log('🔧 Initializing application...');

    // Load products
    loadProducts();

    // Setup event listeners
    setupCategoryButtons();
    setupFilterButtons();
    setupMenuButtons();
    setupCartButtons();
    
    // Setup real-time filtering (with delay to ensure DOM is ready)
    setTimeout(setupFilterButtonsEvents, 500);

    // Load cart
    loadCart();

    console.log('✅ Application initialized');
}

// Load products from JSON
async function loadProducts() {
    try {
        console.log('📦 Loading products...');
        const response = await fetch('JS/productos.json');
        productos = await response.json();
        console.log('✅ Products loaded:', productos.length);

        // Show all products initially
        mostrarProductos(productos);

        // Click "todos" button to set initial state
        const todoBtn = document.getElementById('todos');
        if (todoBtn) {
            todoBtn.click();
        }
    } catch (error) {
        console.error('❌ Error loading products:', error);
        productos = [];
        mostrarProductos([]);
    }
}

// Show products INCLUDING VARIANTS
function mostrarProductos(productosArray) {
    console.log('📦 Showing products:', productosArray.length);

    if (!contenedorProductos) {
        console.error('❌ Product container not found');
        return;
    }

    contenedorProductos.innerHTML = '';

    if (productosArray.length === 0) {
        contenedorProductos.innerHTML = '<p>No hay productos disponibles</p>';
        return;
    }

    productosArray.forEach(producto => {
        // Show ALL products including variants
        const div = document.createElement("div");
        div.classList.add("producto");

        // Check if product is out of stock
        const sinStock = producto.stock <= 0;

        if (sinStock) {
            div.classList.add("producto-sin-stock");
        }

        // Add variant indicator if it's a variant
        const variantBadge = producto.es_variante ? 
            `<div class="variant-badge" style="
                position: absolute;
                top: 8px;
                left: 8px;
                background: #1291da;
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
                z-index: 1;
            ">${producto.variante?.valor || 'Variante'}</div>` : '';

        div.innerHTML = `
            <div class="producto-imagen-container" style="position: relative;">
                <img class="producto-img" src="${producto.imagen}" alt="${producto.titulo}">
                ${variantBadge}
                ${sinStock ? '<div class="sin-stock-overlay">SIN STOCK</div>' : ''}
            </div>
            <div class="producto-detalles">
                <h3 class="producto-titulo">${producto.titulo}</h3>
                <p class="producto-precio">$${producto.precio}</p>
                <button class="producto-consultar ${sinStock ? 'disabled' : ''}" 
                        id="${producto.id}" 
                        ${sinStock ? 'disabled' : ''}>
                    ${sinStock ? 'Sin Stock' : 'Consultar'}
                </button>
            </div>
        `;

        contenedorProductos.append(div);
    });

    // Setup product buttons
    setupProductButtons();
}

// Setup category buttons
function setupCategoryButtons() {
    console.log('🔧 Setting up category buttons...');

    botonesCategoria.forEach(boton => {
        boton.addEventListener("click", (e) => {
            // Remove active from all buttons
            botonesCategoria.forEach(btn => btn.classList.remove("active"));
            // Add active to clicked button
            e.currentTarget.classList.add("active");

            // Update title
            let titulo = "Todos los productos";
            if (e.currentTarget.id === "indumentaria") titulo = "Indumentaria";
            else if (e.currentTarget.id === "accesorios") titulo = "Accesorios";
            else if (e.currentTarget.id !== "todos") titulo = e.currentTarget.textContent.trim();

            if (tituloPrincipal) {
                tituloPrincipal.innerText = titulo;
            }

            // Filter products
            if (e.currentTarget.id !== "todos") {
                const productosBoton = productos.filter(producto => {
                    if (e.currentTarget.id === "indumentaria") {
                        return producto.categoria_general === "indumentaria";
                    } else if (e.currentTarget.id === "accesorios") {
                        return producto.categoria_general === "accesorios";
                    } else {
                        return producto.categoria && producto.categoria.id === e.currentTarget.id;
                    }
                });
                mostrarProductos(productosBoton);
            } else {
                mostrarProductos(productos);
            }

            // Close mobile menu
            const aside = document.querySelector('aside');
            if (aside) {
                aside.classList.remove('aside-visible');
            }
        });
    });

    console.log('✅ Category buttons configured');
}

// Setup filter buttons
function setupFilterButtons() {
    console.log('🔧 Setting up filter buttons...');

    const toggleFiltros = document.getElementById('toggle-filtros');
    const filtros = document.getElementById('filtros');
    const filterClose = document.querySelector('.filter-close');

    if (toggleFiltros && filtros) {
        toggleFiltros.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            console.log('🔄 Filter toggle clicked');

            // Show filters with proper styling
            filtros.style.cssText = `
                display: block !important;
                position: fixed !important;
                top: 120px !important;
                right: 20px !important;
                width: 400px !important;
                max-height: 500px !important;
                background: white !important;
                border: 1px solid #ddd !important;
                border-radius: 8px !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
                z-index: 9999 !important;
                padding: 0 !important;
                color: #333 !important;
                font-size: 14px !important;
                overflow-y: auto !important;
            `;

            console.log('✅ Filters should now be visible');
        });
    }

    // Setup close button functionality
    if (filterClose && filtros) {
        filterClose.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('❌ Filter close clicked');
            filtros.style.display = 'none';
        });
    }

    // Close filters when clicking outside
    document.addEventListener('click', function (e) {
        if (filtros && filtros.style.display === 'block') {
            if (!filtros.contains(e.target) && !toggleFiltros.contains(e.target)) {
                console.log('🖱️ Clicked outside, closing filters');
                filtros.style.display = 'none';
            }
        }
    });

    console.log('✅ Filter buttons configured');
}

// Setup menu buttons
function setupMenuButtons() {
    console.log('🔧 Setting up menu buttons...');

    const openMenu = document.getElementById('open-menu');
    const closeMenu = document.getElementById('close-menu');
    const aside = document.querySelector('aside');

    // Open menu
    if (openMenu && aside) {
        openMenu.addEventListener('click', function (e) {
            e.preventDefault();
            console.log('Open menu clicked');
            aside.classList.add('aside-visible');
        });
    }

    // Close menu
    if (closeMenu && aside) {
        closeMenu.addEventListener('click', function (e) {
            e.preventDefault();
            console.log('Close menu clicked');
            aside.classList.remove('aside-visible');
        });
    }

    console.log('✅ Menu buttons configured');
}

// Setup cart buttons
function setupCartButtons() {
    console.log('🔧 Setting up cart buttons...');

    // Cart link in sidebar
    const cartLink = document.querySelector('.boton-carrito');
    if (cartLink) {
        cartLink.addEventListener('click', function (e) {
            console.log('Cart button clicked');
            // Close mobile menu
            const aside = document.querySelector('aside');
            if (aside) {
                aside.classList.remove('aside-visible');
            }
        });
    }

    console.log('✅ Cart buttons configured');
}

// Load cart from localStorage
function loadCart() {
    try {
        const cartData = localStorage.getItem("productos-en-carrito");
        if (cartData) {
            productosEnCarrito = JSON.parse(cartData);
        } else {
            productosEnCarrito = [];
        }
        actualizarNumerito();
        console.log('✅ Cart loaded:', productosEnCarrito.length, 'items');
    } catch (error) {
        console.error('❌ Error loading cart:', error);
        productosEnCarrito = [];
    }
}

// Update cart counter
function actualizarNumerito() {
    if (numerito) {
        const totalItems = productosEnCarrito.reduce((acc, producto) => acc + producto.cantidad, 0);
        numerito.innerText = totalItems;
    }
}

// Setup product consultation buttons
function setupProductButtons() {
    const botonesAgregar = document.querySelectorAll('.producto-consultar:not(.disabled)');
    botonesAgregar.forEach(boton => {
        boton.addEventListener('click', (e) => {
            const productoId = e.target.id;
            console.log('Product button clicked:', productoId);
            mostrarModalProducto(productoId);
        });
    });
}

// Show product modal
function mostrarModalProducto(productoId) {
    const producto = productos.find(p => p.id === productoId);
    if (!producto) {
        console.error('Producto no encontrado:', productoId);
        return;
    }

    // Don't show modal for out of stock products
    if (producto.stock <= 0) {
        alert('Este producto no tiene stock disponible');
        return;
    }

    console.log('Showing modal for product:', producto);

    // Update modal content
    document.getElementById('modal-titulo').textContent = 'Consultar Producto';
    document.getElementById('modal-nombre').textContent = producto.titulo;
    document.getElementById('modal-precio').textContent = `$${producto.precio}`;
    document.getElementById('modal-imagen').src = producto.imagen;
    document.getElementById('modal-imagen').alt = producto.titulo;
    document.getElementById('modal-stock').textContent = `Stock disponible: ${producto.stock}`;

    // Setup size selector
    const talleSelector = document.getElementById('talle-selector');
    const selectTalle = document.getElementById('select-talle');

    if (producto.talles && producto.talles.length > 0 && producto.talles[0] !== "No") {
        talleSelector.style.display = 'block';
        selectTalle.innerHTML = '<option value="">Selecciona un talle</option>';
        producto.talles.forEach(talle => {
            const option = document.createElement('option');
            option.value = talle;
            option.textContent = talle;
            selectTalle.appendChild(option);
        });
    } else {
        talleSelector.style.display = 'none';
    }

    // Reset quantity
    document.getElementById('cantidad').value = 1;

    // Show modal
    document.getElementById('modal-producto').style.display = 'flex';

    // Setup modal events
    setupModalEvents(producto);
}

// Setup modal events
function setupModalEvents(producto) {
    const modal = document.getElementById('modal-producto');
    const closeBtn = document.getElementById('modal-close');
    const cantidadInput = document.getElementById('cantidad');
    const btnMenos = document.getElementById('btn-menos');
    const btnMas = document.getElementById('btn-mas');
    const btnAgregar = document.getElementById('btn-agregar-carrito');

    // Close modal
    const closeModal = () => {
        modal.style.display = 'none';
    };

    closeBtn.onclick = closeModal;
    modal.onclick = (e) => {
        if (e.target === modal) closeModal();
    };

    // Quantity controls
    btnMenos.onclick = () => {
        const current = parseInt(cantidadInput.value);
        if (current > 1) {
            cantidadInput.value = current - 1;
        }
    };

    btnMas.onclick = () => {
        const current = parseInt(cantidadInput.value);
        const maxStock = Math.min(producto.stock, 10);
        if (current < maxStock) {
            cantidadInput.value = current + 1;
        }
    };

    // Add to cart
    btnAgregar.onclick = () => {
        agregarAlCarrito(producto);
    };
}

// Add to cart function
function agregarAlCarrito(producto) {
    const cantidadInput = document.getElementById('cantidad');
    const selectTalle = document.getElementById('select-talle');
    const cantidad = parseInt(cantidadInput.value);

    // Validate size selection if required
    if (producto.talles && producto.talles.length > 0 && producto.talles[0] !== "No") {
        if (!selectTalle.value) {
            alert('Por favor selecciona un talle');
            return;
        }
    }

    // Validate stock
    if (cantidad > producto.stock) {
        alert(`Solo hay ${producto.stock} unidades disponibles`);
        return;
    }

    // Create cart item
    const talleSeleccionado = selectTalle.value || 'Único';
    const itemId = `${producto.id}_${talleSeleccionado}`;

    // Check if item already exists in cart
    const existingItem = productosEnCarrito.find(item =>
        item.id === producto.id && item.talle === talleSeleccionado
    );

    if (existingItem) {
        // Update quantity
        const newQuantity = existingItem.cantidad + cantidad;
        if (newQuantity > producto.stock) {
            alert(`No puedes agregar más de ${producto.stock} unidades`);
            return;
        }
        existingItem.cantidad = newQuantity;
    } else {
        // Add new item
        const cartItem = {
            ...producto,
            cantidad: cantidad,
            talle: talleSeleccionado,
            cartId: itemId
        };
        productosEnCarrito.push(cartItem);
    }

    // Save to localStorage
    localStorage.setItem("productos-en-carrito", JSON.stringify(productosEnCarrito));

    // Update counter
    actualizarNumerito();

    // Close modal
    document.getElementById('modal-producto').style.display = 'none';

    // Show success message
    mostrarMensajeExito(`${producto.titulo} agregado al carrito`);

    console.log('Product added to cart:', productosEnCarrito);
}

// Show success message
function mostrarMensajeExito(mensaje) {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = 'toast-success';
    toast.innerHTML = `
        <i class="bi bi-check-circle"></i>
        ${mensaje}
    `;

    // Add styles
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
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
    `;

    // Add animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    `;
    document.head.appendChild(style);

    document.body.appendChild(toast);

    // Remove after 3 seconds
    setTimeout(() => {
        toast.remove();
        style.remove();
    }, 3000);
}

// Filter functionality with real-time updates
function aplicarFiltros() {
    // Get filter values
    const nombre = document.getElementById('filtro-nombre')?.value.toLowerCase().trim() || '';
    const categoria = document.getElementById('filtro-categoria')?.value || '';
    const genero = document.getElementById('filtro-genero')?.value || '';
    const talle = document.getElementById('filtro-talle')?.value || '';
    const disciplina = document.getElementById('filtro-disciplina')?.value || '';
    const precioMin = parseFloat(document.getElementById('filtro-precio-min')?.value) || 0;
    const precioMax = parseFloat(document.getElementById('filtro-precio-max')?.value) || Infinity;
    
    // Count active filters
    const filtrosActivos = [nombre, categoria, genero, talle, disciplina].filter(f => f).length + 
                          (precioMin > 0 || precioMax < Infinity ? 1 : 0);
    
    // Show loading indicator
    if (contenedorProductos) {
        contenedorProductos.style.opacity = '0.7';
    }
    
    // Filter products - INCLUDE VARIANTS IN FILTERING
    const productosFiltrados = productos.filter(producto => {
        // Name filter (partial match)
        if (nombre && !producto.titulo.toLowerCase().includes(nombre)) {
            return false;
        }
        
        // Category filter
        if (categoria && producto.categoria?.id !== categoria) {
            return false;
        }
        
        // Gender filter
        if (genero && producto.genero !== genero) {
            return false;
        }
        
        // Size filter
        if (talle && producto.talles && !producto.talles.includes(talle)) {
            return false;
        }
        
        // Sport filter
        if (disciplina && producto.disciplina !== disciplina) {
            return false;
        }
        
        // Price filter
        const precio = parseFloat(producto.precio);
        if (precio < precioMin || precio > precioMax) {
            return false;
        }
        
        return true;
    });
    
    // Update title with filter status
    if (tituloPrincipal) {
        if (filtrosActivos > 0) {
            tituloPrincipal.innerHTML = `
                <span>Productos filtrados</span>
                <small style="color: #1291da; font-weight: normal; margin-left: 10px;">
                    ${productosFiltrados.length} resultado${productosFiltrados.length !== 1 ? 's' : ''} 
                    • ${filtrosActivos} filtro${filtrosActivos !== 1 ? 's' : ''} activo${filtrosActivos !== 1 ? 's' : ''}
                </small>
            `;
        } else {
            tituloPrincipal.innerHTML = "Todos los productos";
        }
    }
    
    // Show filtered products
    mostrarProductos(productosFiltrados);
    
    // Show "no results" message if needed
    if (productosFiltrados.length === 0 && filtrosActivos > 0) {
        mostrarMensajeSinResultados();
    }
    
    // Update filter button indicator
    updateFilterButtonIndicator(filtrosActivos);
    
    // Remove loading indicator
    if (contenedorProductos) {
        contenedorProductos.style.opacity = '1';
    }
    
    console.log(`🔍 Real-time filter: ${productosFiltrados.length}/${productos.length} products, ${filtrosActivos} active filters`);
}

// Show "no results" message
function mostrarMensajeSinResultados() {
    if (!contenedorProductos) return;
    
    contenedorProductos.innerHTML = `
        <div class="no-results-message" style="
            text-align: center;
            padding: 60px 20px;
            color: #666;
            font-size: 16px;
        ">
            <i class="bi bi-search" style="font-size: 48px; color: #ddd; margin-bottom: 20px; display: block;"></i>
            <h3 style="color: #333; margin-bottom: 10px;">No se encontraron productos</h3>
            <p>Intenta ajustar los filtros para encontrar lo que buscas</p>
            <button onclick="limpiarFiltros()" style="
                margin-top: 20px;
                padding: 10px 20px;
                background: #1291da;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
            ">
                <i class="bi bi-arrow-clockwise"></i> Limpiar filtros
            </button>
        </div>
    `;
}

function limpiarFiltros() {
    console.log('🧹 Clearing all filters...');
    
    // Clear all filter inputs
    const inputs = document.querySelectorAll('#filtros input, #filtros select');
    inputs.forEach(input => {
        input.value = '';
    });
    
    // Reset title
    if (tituloPrincipal) {
        tituloPrincipal.innerHTML = "Todos los productos";
    }
    
    // Update filter button indicator
    updateFilterButtonIndicator(0);
    
    // Show all products
    mostrarProductos(productos);
    
    console.log('✅ Filters cleared');
}

// Update filter button to show active filters count
function updateFilterButtonIndicator(activeCount) {
    const toggleBtn = document.getElementById('toggle-filtros');
    if (!toggleBtn) return;
    
    // Remove existing indicator
    const existingIndicator = toggleBtn.querySelector('.filter-indicator');
    if (existingIndicator) {
        existingIndicator.remove();
    }
    
    // Add new indicator if there are active filters
    if (activeCount > 0) {
        const indicator = document.createElement('span');
        indicator.className = 'filter-indicator';
        indicator.textContent = activeCount;
        indicator.style.cssText = `
            position: absolute;
            top: -8px;
            right: -8px;
            background: #dc3545;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            font-size: 12px;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid white;
        `;
        
        // Make button position relative if not already
        toggleBtn.style.position = 'relative';
        toggleBtn.appendChild(indicator);
    }
}

// Setup filter buttons functionality with real-time filtering
function setupFilterButtonsEvents() {
    const applyBtn = document.getElementById('apply-filters');
    const clearBtn = document.getElementById('clear-all-filters');
    
    // Get all filter inputs
    const filterInputs = [
        document.getElementById('filtro-nombre'),
        document.getElementById('filtro-categoria'),
        document.getElementById('filtro-genero'),
        document.getElementById('filtro-talle'),
        document.getElementById('filtro-disciplina'),
        document.getElementById('filtro-precio-min'),
        document.getElementById('filtro-precio-max')
    ].filter(input => input !== null);
    
    console.log('Found filter inputs:', filterInputs.length);
    
    // Add real-time filtering to all inputs
    filterInputs.forEach(input => {
        console.log(`Setting up real-time filter for: ${input.id} (${input.tagName})`);
        
        // For text inputs - filter while typing (with small delay)
        if (input.type === 'text' || input.type === 'number') {
            let timeout;
            input.addEventListener('input', function() {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    console.log(`🔄 Real-time filter: ${input.id} = "${input.value}"`);
                    aplicarFiltros();
                }, 300); // 300ms delay to avoid too many calls while typing
            });
            
            // Also trigger on paste events
            input.addEventListener('paste', function() {
                setTimeout(() => {
                    console.log(`📋 Paste filter: ${input.id} = "${input.value}"`);
                    aplicarFiltros();
                }, 350);
            });
        }
        
        // For select dropdowns - filter immediately on change
        if (input.tagName === 'SELECT') {
            input.addEventListener('change', function() {
                console.log(`🔄 Real-time filter: ${input.id} = "${input.value}"`);
                aplicarFiltros();
            });
        }
    });
    
    // Apply button now just closes the modal (since filtering is automatic)
    if (applyBtn) {
        applyBtn.addEventListener('click', function() {
            console.log('✅ Apply filters clicked - closing modal');
            document.getElementById('filtros').style.display = 'none';
        });
    }
    
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            console.log('🧹 Clear filters clicked');
            limpiarFiltros();
        });
    }
    
    console.log('✅ Real-time filter events configured');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

// Initialize filter buttons when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        setupFilterButtonsEvents();
        console.log('🔧 Real-time filters initialized');
    }, 1000);
});

console.log('✅ main-variants.js loaded');