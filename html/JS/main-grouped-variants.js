// Main.js with grouped variants functionality
console.log('🚀 Loading main-grouped-variants.js...');

// Global variables
let productos = [];
let productosEnCarrito = [];
let productosAgrupados = [];

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

// Load products from JSON and group variants
async function loadProducts() {
    try {
        console.log('📦 Loading products...');
        const response = await fetch('JS/productos.json');
        productos = await response.json();
        console.log('✅ Products loaded:', productos.length);

        // Group products with variants
        productosAgrupados = groupProductsWithVariants(productos);
        console.log('✅ Products grouped:', productosAgrupados.length);

        // Show all products initially
        mostrarProductos(productosAgrupados);

        // Click "todos" button to set initial state
        const todoBtn = document.getElementById('todos');
        if (todoBtn) {
            todoBtn.click();
        }
    } catch (error) {
        console.error('❌ Error loading products:', error);
        productos = [];
        productosAgrupados = [];
        mostrarProductos([]);
    }
}

// Group products with their variants
function groupProductsWithVariants(productosArray) {
    const grouped = [];
    const processedParents = new Set();

    productosArray.forEach(producto => {
        if (producto.es_variante) {
            // This is a variant, check if parent is already processed
            const parentId = producto.producto_padre;
            if (!processedParents.has(parentId)) {
                // Find all variants for this parent
                const variants = productosArray.filter(p =>
                    p.es_variante && p.producto_padre === parentId
                );

                // Find first variant with stock, or default to first variant
                let defaultVariantIndex = 0;
                for (let i = 0; i < variants.length; i++) {
                    if (variants[i].stock > 0) {
                        defaultVariantIndex = i;
                        break;
                    }
                }

                // Create grouped product
                const groupedProduct = {
                    ...variants[defaultVariantIndex], // Use variant with stock as base
                    id: parentId, // Use parent ID
                    titulo: producto.titulo.split(' - ')[0], // Remove variant suffix
                    variantes: variants,
                    selectedVariant: defaultVariantIndex, // Default to variant with stock
                    hasVariants: true
                };

                grouped.push(groupedProduct);
                processedParents.add(parentId);
            }
        } else {
            // This is a regular product (no variants)
            grouped.push({
                ...producto,
                hasVariants: false,
                variantes: []
            });
        }
    });

    return grouped;
}

// Show products with variant selectors
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

    productosArray.forEach((producto, index) => {
        const div = document.createElement("div");
        div.classList.add("producto");
        div.setAttribute('data-product-index', index);

        // Get current variant data
        const currentVariant = producto.hasVariants ?
            producto.variantes[producto.selectedVariant] : producto;

        // Check if product is out of stock
        const sinStock = currentVariant.stock <= 0;

        if (sinStock) {
            div.classList.add("producto-sin-stock");
        }

        // Create variant selector if product has variants
        const variantSelector = producto.hasVariants ? `
            <div class="variant-selector" style="
                position: absolute;
                top: 8px;
                right: 8px;
                z-index: 2;
            ">
                <select class="variant-dropdown" data-product-index="${index}" style="
                    background: rgba(255,255,255,0.9);
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 12px;
                    font-weight: bold;
                    color: #333;
                    cursor: pointer;
                ">
                    ${producto.variantes.map((variant, varIndex) => `
                        <option value="${varIndex}" ${varIndex === producto.selectedVariant ? 'selected' : ''} ${variant.stock <= 0 ? 'disabled' : ''}>
                            ${variant.variante?.valor || `Variante ${varIndex + 1}`}${variant.stock <= 0 ? ' (Sin stock)' : ''}
                        </option>
                    `).join('')}
                </select>
            </div>
        ` : '';

        div.innerHTML = `
            <div class="producto-imagen-container" style="position: relative;">
                <img class="producto-img" src="${currentVariant.imagen}" alt="${currentVariant.titulo}">
                ${variantSelector}
                ${sinStock ? '<div class="sin-stock-overlay">SIN STOCK</div>' : ''}
            </div>
            <div class="producto-detalles">
                <h3 class="producto-titulo">${producto.titulo}</h3>
                <p class="producto-precio">$${currentVariant.precio}</p>
                ${producto.hasVariants ? `<p class="variant-info" style="font-size: 12px; color: #666; margin: 4px 0;">
                    ${currentVariant.variante?.valor || 'Variante'}
                </p>` : ''}
                <button class="producto-consultar ${sinStock ? 'disabled' : ''}" 
                        id="${currentVariant.id}" 
                        ${sinStock ? 'disabled' : ''}>
                    ${sinStock ? 'Sin Stock' : 'Consultar'}
                </button>
            </div>
        `;

        contenedorProductos.append(div);
    });

    // Setup product buttons and variant selectors
    setupProductButtons();
    setupVariantSelectors();
}

// Setup variant selector dropdowns
function setupVariantSelectors() {
    const variantDropdowns = document.querySelectorAll('.variant-dropdown');

    variantDropdowns.forEach(dropdown => {
        // Store the previous valid selection
        let previousValidSelection = dropdown.value;
        
        dropdown.addEventListener('change', function (e) {
            const productIndex = parseInt(e.target.getAttribute('data-product-index'));
            const selectedVariantIndex = parseInt(e.target.value);
            const selectedVariant = productosAgrupados[productIndex].variantes[selectedVariantIndex];

            // Check if selected variant has stock
            if (selectedVariant.stock <= 0) {
                // Show message and revert to previous selection
                alert(`La variante "${selectedVariant.variante?.valor}" no tiene stock disponible.`);
                e.target.value = previousValidSelection;
                return;
            }

            // Update previous valid selection
            previousValidSelection = selectedVariantIndex;

            // Update selected variant
            productosAgrupados[productIndex].selectedVariant = selectedVariantIndex;

            // Re-render just this product
            const productDiv = document.querySelector(`[data-product-index="${productIndex}"]`);
            const producto = productosAgrupados[productIndex];
            const currentVariant = producto.variantes[selectedVariantIndex];

            // Update image
            const img = productDiv.querySelector('.producto-img');
            img.src = currentVariant.imagen;
            img.alt = currentVariant.titulo;

            // Update price
            const precio = productDiv.querySelector('.producto-precio');
            precio.textContent = `$${currentVariant.precio}`;

            // Update variant info
            const variantInfo = productDiv.querySelector('.variant-info');
            if (variantInfo) {
                variantInfo.textContent = `${currentVariant.variante?.valor || 'Variante'}`;
            }

            // Update button
            const button = productDiv.querySelector('.producto-consultar');
            const sinStock = currentVariant.stock <= 0;

            button.id = currentVariant.id;
            button.disabled = sinStock;
            button.textContent = sinStock ? 'Sin Stock' : 'Consultar';
            button.className = `producto-consultar ${sinStock ? 'disabled' : ''}`;

            // Update stock overlay
            const stockOverlay = productDiv.querySelector('.sin-stock-overlay');
            const imageContainer = productDiv.querySelector('.producto-imagen-container');
            
            if (sinStock && !stockOverlay && imageContainer) {
                const overlay = document.createElement('div');
                overlay.className = 'sin-stock-overlay';
                overlay.textContent = 'SIN STOCK';
                overlay.style.cssText = `
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(255, 255, 255, 0.8);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    color: #dc3545;
                    font-size: 14px;
                    z-index: 1;
                `;
                imageContainer.appendChild(overlay);
            } else if (!sinStock && stockOverlay) {
                stockOverlay.remove();
            }

            // Update product div class
            if (sinStock) {
                productDiv.classList.add('producto-sin-stock');
            } else {
                productDiv.classList.remove('producto-sin-stock');
            }

            console.log(`🔄 Variant changed: ${producto.titulo} -> ${currentVariant.variante?.valor}`);
        });
    });

    console.log('✅ Variant selectors configured:', variantDropdowns.length);
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
                const productosBoton = productosAgrupados.filter(producto => {
                    const currentVariant = producto.hasVariants ?
                        producto.variantes[producto.selectedVariant] : producto;

                    if (e.currentTarget.id === "indumentaria") {
                        return currentVariant.categoria_general === "indumentaria";
                    } else if (e.currentTarget.id === "accesorios") {
                        return currentVariant.categoria_general === "accesorios";
                    } else {
                        return currentVariant.categoria && currentVariant.categoria.id === e.currentTarget.id;
                    }
                });
                mostrarProductos(productosBoton);
            } else {
                mostrarProductos(productosAgrupados);
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

    console.log('Filter elements found:', {
        toggleFiltros: !!toggleFiltros,
        filtros: !!filtros,
        filterClose: !!filterClose
    });

    if (toggleFiltros && filtros) {
        // Remove any existing event listeners
        toggleFiltros.replaceWith(toggleFiltros.cloneNode(true));
        const newToggleFiltros = document.getElementById('toggle-filtros');
        
        newToggleFiltros.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            console.log('🔄 Filter toggle clicked');
            console.log('Current filtros display:', filtros.style.display);
            console.log('Filtros element:', filtros);

            // Show filters with proper styling
            filtros.style.cssText = `
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
                position: fixed !important;
                top: 120px !important;
                right: 20px !important;
                width: 400px !important;
                max-height: 500px !important;
                background: white !important;
                border: 1px solid #ddd !important;
                border-radius: 8px !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
                z-index: 99999 !important;
                padding: 20px !important;
                color: #333 !important;
                font-size: 14px !important;
                overflow-y: auto !important;
            `;

            // Remove any conflicting classes
            filtros.classList.remove('filtros-ocultos');
            filtros.style.visibility = 'visible';
            filtros.style.opacity = '1';

            console.log('✅ Filters should now be visible');
            console.log('New filtros display:', filtros.style.display);
            console.log('Computed styles:', window.getComputedStyle(filtros).display);
            console.log('Element classes:', filtros.className);
        });
    } else {
        console.error('❌ Filter elements not found!');
    }

    // Setup close button functionality
    if (filterClose && filtros) {
        filterClose.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('❌ Filter close clicked');
            filtros.style.display = 'none';
            filtros.style.visibility = 'hidden';
            filtros.style.opacity = '0';
        });
    }

    // Close filters when clicking outside - improved version
    document.addEventListener('click', function (e) {
        const currentToggle = document.getElementById('toggle-filtros');
        const currentFiltros = document.getElementById('filtros');
        
        if (currentFiltros && (currentFiltros.style.display === 'block' || window.getComputedStyle(currentFiltros).display === 'block')) {
            if (!currentFiltros.contains(e.target) && !currentToggle.contains(e.target)) {
                console.log('🖱️ Clicked outside, closing filters');
                currentFiltros.style.display = 'none';
                currentFiltros.style.visibility = 'hidden';
                currentFiltros.style.opacity = '0';
            }
        }
    });

    console.log('✅ Filter buttons configured');
    
    // Backup event listener - direct approach
    setTimeout(() => {
        const backupToggle = document.getElementById('toggle-filtros');
        const backupFiltros = document.getElementById('filtros');
        
        if (backupToggle && backupFiltros) {
            console.log('🔧 Setting up backup filter toggle...');
            
            backupToggle.onclick = function(e) {
                e.preventDefault();
                console.log('🔄 Backup filter toggle activated');
                console.log('Backup filtros element:', backupFiltros);
                
                // Force visibility with multiple methods
                backupFiltros.style.display = 'block';
                backupFiltros.style.visibility = 'visible';
                backupFiltros.style.opacity = '1';
                backupFiltros.classList.remove('filtros-ocultos');
                
                // Apply all styles
                backupFiltros.style.cssText = `
                    display: block !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                    position: fixed !important;
                    top: 120px !important;
                    right: 20px !important;
                    width: 400px !important;
                    max-height: 500px !important;
                    background: white !important;
                    border: 1px solid #ddd !important;
                    border-radius: 8px !important;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
                    z-index: 99999 !important;
                    padding: 20px !important;
                    color: #333 !important;
                    font-size: 14px !important;
                    overflow-y: auto !important;
                `;
                
                console.log('Backup applied. Display:', backupFiltros.style.display);
                console.log('Computed display:', window.getComputedStyle(backupFiltros).display);
            };
        }
    }, 2000);
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
    // Find the product in the original products array (including variants)
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

<<<<<<< Updated upstream
    // Reset quantity
    document.getElementById('cantidad').value = 1;
=======
    // Reset quantity and set max to product stock
    const cantidadInput = document.getElementById('cantidad');
    cantidadInput.value = 1;
    cantidadInput.max = producto.stock;
>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
=======
    const btnMasExtra = document.getElementById('btn-mas-extra');
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
        const maxStock = Math.min(producto.stock, 10);
=======
        const maxStock = producto.stock; // Usar todo el stock disponible
        if (current < maxStock) {
            cantidadInput.value = current + 1;
        }
    };

    // Extra plus button functionality
    btnMasExtra.onclick = () => {
        const current = parseInt(cantidadInput.value);
        const maxStock = producto.stock; // Usar todo el stock disponible
>>>>>>> Stashed changes
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

// Filter functionality with grouped products
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

    // Filter grouped products
    const productosFiltrados = productosAgrupados.filter(producto => {
        const currentVariant = producto.hasVariants ?
            producto.variantes[producto.selectedVariant] : producto;

        // Name filter (partial match)
        if (nombre && !producto.titulo.toLowerCase().includes(nombre)) {
            return false;
        }

        // Category filter
        if (categoria && currentVariant.categoria?.id !== categoria) {
            return false;
        }

        // Gender filter
        if (genero && currentVariant.genero !== genero) {
            return false;
        }

        // Size filter
        if (talle && currentVariant.talles && !currentVariant.talles.includes(talle)) {
            return false;
        }

        // Sport filter
        if (disciplina && currentVariant.disciplina !== disciplina) {
            return false;
        }

        // Price filter
        const precio = parseFloat(currentVariant.precio);
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

    console.log(`🔍 Real-time filter: ${productosFiltrados.length}/${productosAgrupados.length} products, ${filtrosActivos} active filters`);
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
    mostrarProductos(productosAgrupados);

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
            input.addEventListener('input', function () {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    console.log(`🔄 Real-time filter: ${input.id} = "${input.value}"`);
                    aplicarFiltros();
                }, 300); // 300ms delay to avoid too many calls while typing
            });

            // Also trigger on paste events
            input.addEventListener('paste', function () {
                setTimeout(() => {
                    console.log(`📋 Paste filter: ${input.id} = "${input.value}"`);
                    aplicarFiltros();
                }, 350);
            });
        }

        // For select dropdowns - filter immediately on change
        if (input.tagName === 'SELECT') {
            input.addEventListener('change', function () {
                console.log(`🔄 Real-time filter: ${input.id} = "${input.value}"`);
                aplicarFiltros();
            });
        }
    });

    // Apply button now just closes the modal (since filtering is automatic)
    if (applyBtn) {
        applyBtn.addEventListener('click', function () {
            console.log('✅ Apply filters clicked - closing modal');
            const filtrosPanel = document.getElementById('filtros');
            if (filtrosPanel) {
                filtrosPanel.style.display = 'none';
                filtrosPanel.style.visibility = 'hidden';
                filtrosPanel.style.opacity = '0';
            }
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', function () {
            console.log('🧹 Clear filters clicked');
            limpiarFiltros();
            // Optionally close the panel after clearing
            setTimeout(() => {
                const filtrosPanel = document.getElementById('filtros');
                if (filtrosPanel) {
                    filtrosPanel.style.display = 'none';
                    filtrosPanel.style.visibility = 'hidden';
                    filtrosPanel.style.opacity = '0';
                }
            }, 500); // Small delay to see the filters being cleared
        });
    }

    console.log('✅ Real-time filter events configured');
}

// Add CSS styles for disabled options
function addVariantStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .variant-dropdown option:disabled {
            color: #999 !important;
            background-color: #f5f5f5 !important;
            font-style: italic;
        }
        
        .variant-dropdown option:disabled:hover {
            background-color: #f5f5f5 !important;
            cursor: not-allowed;
        }
    `;
    document.head.appendChild(style);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        addVariantStyles();
        initializeApp();
        // Initialize filters after a short delay
        setTimeout(() => {
            setupFilterButtonsEvents();
            console.log('🔧 Real-time filters initialized');
        }, 1000);
    });
} else {
    addVariantStyles();
    initializeApp();
    // Initialize filters immediately if DOM is already ready
    setTimeout(() => {
        setupFilterButtonsEvents();
        console.log('🔧 Real-time filters initialized');
    }, 500);
}

console.log('✅ main-grouped-variants.js loaded');