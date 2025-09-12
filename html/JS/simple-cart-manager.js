/**
 * Simplified Cart Data Manager
 * Handles all cart operations with robust error handling and localStorage persistence
 */
class CartDataManager {
    constructor() {
        console.log('🔄 CartDataManager constructor called');
        
        this.storageKey = 'productos-en-carrito';
        this.fallbackCart = [];
        
        try {
            this.isStorageAvailable = this.checkStorageAvailability();
            console.log('✅ Storage availability check completed:', this.isStorageAvailable);
        } catch (error) {
            console.error('❌ Storage availability check failed:', error);
            this.isStorageAvailable = false;
        }
        
        // Initialize with data validation and migration (delayed to avoid blocking)
        setTimeout(() => {
            try {
                this.initializeStorage();
            } catch (error) {
                console.error('❌ Storage initialization failed:', error);
            }
        }, 100);
        
        console.log('✅ CartDataManager constructor completed');
    }

    /**
     * Initialize storage with validation and migration
     */
    initializeStorage() {
        try {
            console.log('🔄 Initializing cart storage...');
            
            // Validate storage integrity first
            const isValid = this.validateStorageIntegrity();
            
            if (!isValid) {
                console.warn('Storage validation failed, attempting backup restore...');
                const restored = this.restoreFromBackup();
                
                if (!restored) {
                    console.log('No backup available, starting with empty cart');
                }
            }
            
            // Migrate existing data to include size structure
            this.migrateCartSizeData();
            
            // Create backup of current state
            this.createBackup();
            
            console.log('✅ Cart storage initialized successfully');
        } catch (error) {
            console.error('❌ Error initializing storage:', error);
        }
    }

    /**
     * Check if localStorage is available
     */
    checkStorageAvailability() {
        try {
            const test = '__storage_test__';
            localStorage.setItem(test, test);
            localStorage.removeItem(test);
            return true;
        } catch (e) {
            console.warn('localStorage not available, using fallback storage');
            return false;
        }
    }

    /**
     * Load cart from storage with error handling
     */
    loadCart() {
        try {
            if (!this.isStorageAvailable) {
                return [...this.fallbackCart];
            }

            const cartData = localStorage.getItem(this.storageKey);
            if (!cartData) {
                return [];
            }

            const parsedCart = JSON.parse(cartData);
            
            // Validate cart data structure
            if (!Array.isArray(parsedCart)) {
                console.warn('Invalid cart data structure, resetting cart');
                this.clearCart();
                return [];
            }

            // Validate each product in cart
            const validatedCart = parsedCart.filter(product => this.validateProduct(product));
            
            // If some products were invalid, save the cleaned cart
            if (validatedCart.length !== parsedCart.length) {
                console.warn('Some cart products were invalid and removed');
                this.saveCart(validatedCart);
            }

            return validatedCart;
        } catch (error) {
            console.error('Error loading cart:', error);
            this.clearCart(); // Clear corrupted data
            return [];
        }
    }

    /**
     * Save cart to storage with enhanced size data handling and backup
     */
    saveCart(products) {
        try {
            if (!Array.isArray(products)) {
                console.error('Invalid products array provided to saveCart');
                return false;
            }

            // Create backup before saving
            this.createBackup();

            // Validate all products and clean up size data
            const validProducts = products.filter(product => {
                const isValid = this.validateProduct(product);
                
                if (isValid) {
                    // Ensure size data consistency
                    this.normalizeSizeData(product);
                }
                
                return isValid;
            });

            // Log size data changes if any products were filtered out
            if (validProducts.length !== products.length) {
                console.warn(`Filtered out ${products.length - validProducts.length} invalid products during save`);
            }

            // Attempt to save with retry logic
            let saveSuccess = false;
            let retryCount = 0;
            const maxRetries = 3;

            while (!saveSuccess && retryCount < maxRetries) {
                try {
                    if (this.isStorageAvailable) {
                        // Check available storage space
                        const dataString = JSON.stringify(validProducts);
                        
                        // Estimate storage usage (rough calculation)
                        const estimatedSize = new Blob([dataString]).size;
                        
                        if (estimatedSize > 5 * 1024 * 1024) { // 5MB limit
                            console.warn('Cart data is very large, may cause storage issues');
                        }
                        
                        localStorage.setItem(this.storageKey, dataString);
                        
                        // Verify the save was successful
                        const savedData = localStorage.getItem(this.storageKey);
                        if (savedData === dataString) {
                            saveSuccess = true;
                        } else {
                            throw new Error('Data verification failed after save');
                        }
                    } else {
                        this.fallbackCart = [...validProducts];
                        saveSuccess = true;
                    }
                } catch (saveError) {
                    retryCount++;
                    console.warn(`Save attempt ${retryCount} failed:`, saveError);
                    
                    if (retryCount >= maxRetries) {
                        // Try to clear some space and retry once more
                        if (this.isStorageAvailable) {
                            try {
                                // Remove old backups
                                localStorage.removeItem(`${this.storageKey}_backup`);
                                localStorage.setItem(this.storageKey, JSON.stringify(validProducts));
                                saveSuccess = true;
                            } catch (finalError) {
                                console.error('Final save attempt failed:', finalError);
                                // Fall back to in-memory storage
                                this.fallbackCart = [...validProducts];
                                this.isStorageAvailable = false;
                                saveSuccess = true;
                            }
                        }
                    } else {
                        // Wait before retry (using setTimeout instead of await)
                        setTimeout(() => {}, 100 * retryCount);
                    }
                }
            }

            if (saveSuccess) {
                console.log(`✅ Cart saved successfully with ${validProducts.length} products`);
            }

            return saveSuccess;
        } catch (error) {
            console.error('Error saving cart:', error);
            
            // Emergency fallback
            try {
                this.fallbackCart = [...products];
                this.isStorageAvailable = false;
                console.log('⚠️ Using emergency fallback storage');
                return true;
            } catch (fallbackError) {
                console.error('Emergency fallback failed:', fallbackError);
                return false;
            }
        }
    }

    /**
     * Normalize size data for a product to ensure consistency
     * @param {Object} product - The product to normalize
     */
    normalizeSizeData(product) {
        try {
            // Ensure talles array exists and is valid
            if (!product.talles || !Array.isArray(product.talles)) {
                product.talles = [];
            }

            // Ensure tallesSeleccionados array exists and is valid
            if (!product.tallesSeleccionados || !Array.isArray(product.tallesSeleccionados)) {
                product.tallesSeleccionados = [];
            }

            // Remove any selected sizes that are not in available sizes
            if (product.talles.length > 0) {
                product.tallesSeleccionados = product.tallesSeleccionados.filter(selected => 
                    product.talles.includes(selected)
                );
            } else {
                // If no available sizes, clear selected sizes
                product.tallesSeleccionados = [];
            }

            // Remove duplicates from both arrays
            product.talles = [...new Set(product.talles)];
            product.tallesSeleccionados = [...new Set(product.tallesSeleccionados)];

            // Add timestamp for size data tracking
            if (product.tallesSeleccionados.length > 0 && !product.lastSizeUpdate) {
                product.lastSizeUpdate = Date.now();
            }

        } catch (error) {
            console.error('Error normalizing size data:', error);
            // Fallback: clear size data if normalization fails
            product.talles = [];
            product.tallesSeleccionados = [];
        }
    }

    /**
     * Validate product data structure
     */
    validateProduct(product) {
        if (!product || typeof product !== 'object') {
            return false;
        }

        // Required fields
        const requiredFields = ['id', 'titulo', 'precio'];
        for (const field of requiredFields) {
            if (!product.hasOwnProperty(field) || product[field] === null || product[field] === undefined) {
                console.warn(`Product missing required field: ${field}`, product);
                return false;
            }
        }

        // Validate data types
        if (typeof product.id !== 'string' || product.id.trim() === '') {
            return false;
        }

        if (typeof product.titulo !== 'string' || product.titulo.trim() === '') {
            return false;
        }

        if (typeof product.precio !== 'number' && typeof product.precio !== 'string') {
            return false;
        }

        // Ensure cantidad is a positive number
        if (product.cantidad !== undefined) {
            const cantidad = Number(product.cantidad);
            if (isNaN(cantidad) || cantidad < 1) {
                return false;
            }
            product.cantidad = cantidad; // Normalize to number
        }

        // Normalize precio to number
        if (typeof product.precio === 'string') {
            const precio = parseFloat(product.precio);
            if (isNaN(precio) || precio < 0) {
                return false;
            }
            product.precio = precio;
        }

        // Validate size data if present
        if (product.talles !== undefined) {
            if (!Array.isArray(product.talles)) {
                console.warn('Product talles must be an array', product);
                product.talles = [];
            } else {
                // Filter out invalid sizes and normalize
                product.talles = product.talles.filter(talle => 
                    typeof talle === 'string' && talle.trim() !== '' && talle !== 'No'
                );
            }
        }

        // Validate selected sizes if present
        if (product.tallesSeleccionados !== undefined) {
            if (!Array.isArray(product.tallesSeleccionados)) {
                console.warn('Product tallesSeleccionados must be an array', product);
                product.tallesSeleccionados = [];
            } else {
                // Ensure selected sizes are valid and available
                const availableSizes = product.talles || [];
                product.tallesSeleccionados = product.tallesSeleccionados.filter(talle => 
                    typeof talle === 'string' && 
                    talle.trim() !== '' && 
                    availableSizes.includes(talle)
                );
            }
        }

        return true;
    }

    /**
     * Add product to cart or update quantity if exists
     */
    addProduct(product) {
        try {
            console.log('🛒 Adding product to cart:', product);
            
            const isValid = this.validateProduct(product);
            console.log('Product validation result:', isValid);
            
            if (!isValid) {
                console.error('Invalid product data provided to addProduct:', product);
                return false;
            }

            const cart = this.loadCart();
            console.log('Current cart before adding:', cart);
            
            const existingIndex = cart.findIndex(item => item.id === product.id);
            console.log('Existing product index:', existingIndex);

            if (existingIndex >= 0) {
                // Update existing product quantity
                const oldQuantity = cart[existingIndex].cantidad || 1;
                const addQuantity = product.cantidad || 1;
                cart[existingIndex].cantidad = oldQuantity + addQuantity;
                console.log(`Updated existing product quantity: ${oldQuantity} + ${addQuantity} = ${cart[existingIndex].cantidad}`);
            } else {
                // Add new product
                const newProduct = {
                    ...product,
                    cantidad: product.cantidad || 1,
                    addedAt: Date.now()
                };
                cart.push(newProduct);
                console.log('Added new product:', newProduct);
            }

            const saveResult = this.saveCart(cart);
            console.log('Save cart result:', saveResult);
            
            if (saveResult) {
                const updatedCart = this.loadCart();
                console.log('Cart after saving:', updatedCart);
            }
            
            return saveResult;
        } catch (error) {
            console.error('Error adding product to cart:', error);
            return false;
        }
    }

    /**
     * Remove product from cart
     */
    removeProduct(productId) {
        try {
            if (!productId || typeof productId !== 'string') {
                console.error('Invalid product ID provided to removeProduct');
                return false;
            }

            const cart = this.loadCart();
            const filteredCart = cart.filter(item => item.id !== productId);
            
            return this.saveCart(filteredCart);
        } catch (error) {
            console.error('Error removing product from cart:', error);
            return false;
        }
    }

    /**
     * Update product quantity
     */
    updateQuantity(productId, newQuantity) {
        try {
            if (!productId || typeof productId !== 'string') {
                console.error('Invalid product ID provided to updateQuantity');
                return false;
            }

            const quantity = Number(newQuantity);
            if (isNaN(quantity) || quantity < 0) {
                console.error('Invalid quantity provided to updateQuantity');
                return false;
            }

            const cart = this.loadCart();
            const productIndex = cart.findIndex(item => item.id === productId);

            if (productIndex === -1) {
                console.warn('Product not found in cart for quantity update');
                return false;
            }

            if (quantity === 0) {
                // Remove product if quantity is 0
                return this.removeProduct(productId);
            } else {
                // Update quantity
                cart[productIndex].cantidad = quantity;
                return this.saveCart(cart);
            }
        } catch (error) {
            console.error('Error updating product quantity:', error);
            return false;
        }
    }

    /**
     * Update product sizes (selected sizes) for a specific product
     * @param {string} productId - The product ID
     * @param {Array} selectedSizes - Array of selected size strings
     * @returns {boolean} Success status
     */
    updateProductSizes(productId, selectedSizes = []) {
        try {
            if (!productId || typeof productId !== 'string') {
                console.error('Invalid product ID provided to updateProductSizes');
                return false;
            }

            if (!Array.isArray(selectedSizes)) {
                console.error('Selected sizes must be an array');
                return false;
            }

            const cart = this.loadCart();
            const productIndex = cart.findIndex(item => item.id === productId);

            if (productIndex === -1) {
                console.warn('Product not found in cart for size update');
                return false;
            }

            const product = cart[productIndex];
            const availableSizes = product.talles || [];

            // Validate that all selected sizes are available
            const validSelectedSizes = selectedSizes.filter(size => 
                typeof size === 'string' && 
                size.trim() !== '' && 
                availableSizes.includes(size)
            );

            // Update the product with validated selected sizes
            cart[productIndex].tallesSeleccionados = validSelectedSizes;
            cart[productIndex].lastSizeUpdate = Date.now();

            const success = this.saveCart(cart);
            
            if (success) {
                console.log(`✅ Updated sizes for ${product.titulo}:`, validSelectedSizes);
            }

            return success;
        } catch (error) {
            console.error('Error updating product sizes:', error);
            return false;
        }
    }

    /**
     * Get product sizes (both available and selected) for a specific product
     * @param {string} productId - The product ID
     * @returns {Object} Object with available and selected sizes, or null if not found
     */
    getProductSizes(productId) {
        try {
            if (!productId || typeof productId !== 'string') {
                console.error('Invalid product ID provided to getProductSizes');
                return null;
            }

            const cart = this.loadCart();
            const product = cart.find(item => item.id === productId);

            if (!product) {
                console.warn('Product not found in cart for size retrieval');
                return null;
            }

            return {
                available: product.talles || [],
                selected: product.tallesSeleccionados || [],
                lastUpdated: product.lastSizeUpdate || null
            };
        } catch (error) {
            console.error('Error getting product sizes:', error);
            return null;
        }
    }

    /**
     * Get all products with their size information
     * @returns {Array} Array of products with size data
     */
    getAllProductSizes() {
        try {
            const cart = this.loadCart();
            
            return cart.map(product => ({
                id: product.id,
                titulo: product.titulo,
                available: product.talles || [],
                selected: product.tallesSeleccionados || [],
                lastUpdated: product.lastSizeUpdate || null
            }));
        } catch (error) {
            console.error('Error getting all product sizes:', error);
            return [];
        }
    }

    /**
     * Validate size selection for a product
     * @param {string} productId - The product ID
     * @param {Array} sizesToValidate - Array of sizes to validate
     * @returns {boolean} Whether all sizes are valid for this product
     */
    validateProductSizes(productId, sizesToValidate = []) {
        try {
            if (!productId || typeof productId !== 'string') {
                return false;
            }

            if (!Array.isArray(sizesToValidate)) {
                return false;
            }

            const productSizes = this.getProductSizes(productId);
            if (!productSizes) {
                return false;
            }

            // Check if all sizes to validate are available
            return sizesToValidate.every(size => 
                typeof size === 'string' && 
                size.trim() !== '' && 
                productSizes.available.includes(size)
            );
        } catch (error) {
            console.error('Error validating product sizes:', error);
            return false;
        }
    }

    /**
     * Clear selected sizes for a specific product
     * @param {string} productId - The product ID
     * @returns {boolean} Success status
     */
    clearProductSizes(productId) {
        try {
            return this.updateProductSizes(productId, []);
        } catch (error) {
            console.error('Error clearing product sizes:', error);
            return false;
        }
    }

    /**
     * Validate and repair localStorage data integrity
     * @returns {boolean} Success status
     */
    validateStorageIntegrity() {
        try {
            if (!this.isStorageAvailable) {
                console.log('localStorage not available, using fallback storage');
                return true;
            }

            const cartData = localStorage.getItem(this.storageKey);
            if (!cartData) {
                return true; // Empty cart is valid
            }

            // Test if data can be parsed
            let parsedData;
            try {
                parsedData = JSON.parse(cartData);
            } catch (parseError) {
                console.error('Corrupted cart data detected, clearing storage');
                localStorage.removeItem(this.storageKey);
                return false;
            }

            // Validate data structure
            if (!Array.isArray(parsedData)) {
                console.error('Invalid cart data structure, clearing storage');
                localStorage.removeItem(this.storageKey);
                return false;
            }

            // Validate each product and clean up corrupted entries
            const validProducts = parsedData.filter(product => {
                const isValid = this.validateProduct(product);
                if (!isValid) {
                    console.warn('Removing corrupted product from cart:', product);
                }
                return isValid;
            });

            // Save cleaned data if any products were removed
            if (validProducts.length !== parsedData.length) {
                console.log(`Cleaned ${parsedData.length - validProducts.length} corrupted products from cart`);
                localStorage.setItem(this.storageKey, JSON.stringify(validProducts));
            }

            return true;
        } catch (error) {
            console.error('Error validating storage integrity:', error);
            // Clear storage on critical error
            try {
                localStorage.removeItem(this.storageKey);
            } catch (clearError) {
                console.error('Failed to clear corrupted storage:', clearError);
            }
            return false;
        }
    }

    /**
     * Create backup of cart data
     * @returns {string|null} Backup data or null if failed
     */
    createBackup() {
        try {
            const cart = this.loadCart();
            const backup = {
                timestamp: Date.now(),
                version: '1.0',
                data: cart
            };
            
            const backupString = JSON.stringify(backup);
            
            // Store backup in localStorage with different key
            if (this.isStorageAvailable) {
                localStorage.setItem(`${this.storageKey}_backup`, backupString);
            }
            
            return backupString;
        } catch (error) {
            console.error('Error creating cart backup:', error);
            return null;
        }
    }

    /**
     * Restore cart from backup
     * @returns {boolean} Success status
     */
    restoreFromBackup() {
        try {
            if (!this.isStorageAvailable) {
                console.warn('Cannot restore backup: localStorage not available');
                return false;
            }

            const backupData = localStorage.getItem(`${this.storageKey}_backup`);
            if (!backupData) {
                console.warn('No backup data found');
                return false;
            }

            const backup = JSON.parse(backupData);
            
            // Validate backup structure
            if (!backup.data || !Array.isArray(backup.data)) {
                console.error('Invalid backup data structure');
                return false;
            }

            // Validate backup age (don't restore backups older than 24 hours)
            const backupAge = Date.now() - backup.timestamp;
            const maxAge = 24 * 60 * 60 * 1000; // 24 hours
            
            if (backupAge > maxAge) {
                console.warn('Backup is too old, not restoring');
                return false;
            }

            // Restore the data
            const success = this.saveCart(backup.data);
            
            if (success) {
                console.log('✅ Cart restored from backup');
            }
            
            return success;
        } catch (error) {
            console.error('Error restoring from backup:', error);
            return false;
        }
    }

    /**
     * Migrate existing cart items to include size data structure
     * This method ensures backward compatibility with existing cart data
     * @returns {boolean} Success status
     */
    migrateCartSizeData() {
        try {
            const cart = this.loadCart();
            let migrationNeeded = false;

            const migratedCart = cart.map(product => {
                // Check if product needs size data migration
                if (!product.hasOwnProperty('talles')) {
                    product.talles = [];
                    migrationNeeded = true;
                }

                if (!product.hasOwnProperty('tallesSeleccionados')) {
                    product.tallesSeleccionados = [];
                    migrationNeeded = true;
                }

                // Normalize existing size data
                this.normalizeSizeData(product);

                return product;
            });

            if (migrationNeeded) {
                console.log('🔄 Migrating cart data to include size structure');
                const success = this.saveCart(migratedCart);
                
                if (success) {
                    console.log('✅ Cart size data migration completed');
                } else {
                    console.error('❌ Cart size data migration failed');
                }
                
                return success;
            }

            return true; // No migration needed
        } catch (error) {
            console.error('Error migrating cart size data:', error);
            return false;
        }
    }

    /**
     * Clear entire cart
     */
    clearCart() {
        try {
            if (this.isStorageAvailable) {
                localStorage.removeItem(this.storageKey);
            } else {
                this.fallbackCart = [];
            }
            return true;
        } catch (error) {
            console.error('Error clearing cart:', error);
            return false;
        }
    }

    /**
<<<<<<< Updated upstream
=======
     * Find product by ID in the global products array
     * @param {string} productId - The product ID to find
     * @returns {Object|null} Product object or null if not found
     */
    findProductById(productId) {
        try {
            // Check in grouped products first
            if (typeof productosAgrupados !== 'undefined' && productosAgrupados.length > 0) {
                for (const producto of productosAgrupados) {
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
            }

            // Fallback: search in original products array
            if (typeof productos !== 'undefined') {
                return productos.find(p => p.id === productId);
            }

            return null;
        } catch (error) {
            console.error('Error finding product by ID:', error);
            return null;
        }
    }

    /**
     * Show stock limit message to user
     * @param {string} productTitle - Product title
     * @param {number} availableStock - Available stock
     */
    showStockMessage(productTitle, availableStock) {
        try {
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
        } catch (error) {
            console.error('Error showing stock message:', error);
        }
    }

    /**
     * Increase product quantity with stock validation
     * @param {string} productId - The product ID
     * @returns {boolean} Success status
     */
    increaseQuantity(productId) {
        try {
            const cart = this.loadCart();
            const item = cart.find(p => p.id === productId);
            
            if (!item) {
                console.warn('Product not found in cart for quantity increase');
                return false;
            }

            // Find product data to check stock
            const producto = this.findProductById(productId);
            if (!producto) {
                console.warn('Product data not found for stock validation');
                return false;
            }

            // Check stock limit
            if (item.cantidad >= producto.stock) {
                this.showStockMessage(producto.titulo, producto.stock);
                return false;
            }

            // Increase quantity
            item.cantidad++;
            const success = this.saveCart(cart);
            
            if (success) {
                console.log(`✅ Increased quantity for ${producto.titulo}: ${item.cantidad}`);
            }
            
            return success;
        } catch (error) {
            console.error('Error increasing quantity:', error);
            return false;
        }
    }

    /**
     * Decrease product quantity
     * @param {string} productId - The product ID
     * @returns {boolean} Success status
     */
    decreaseQuantity(productId) {
        try {
            const cart = this.loadCart();
            const item = cart.find(p => p.id === productId);
            
            if (!item) {
                console.warn('Product not found in cart for quantity decrease');
                return false;
            }

            if (item.cantidad <= 1) {
                // Remove item if quantity would be 0
                return this.removeProduct(productId);
            }

            // Decrease quantity
            item.cantidad--;
            const success = this.saveCart(cart);
            
            if (success) {
                console.log(`✅ Decreased quantity for ${item.titulo}: ${item.cantidad}`);
            }
            
            return success;
        } catch (error) {
            console.error('Error decreasing quantity:', error);
            return false;
        }
    }

    /**
     * Validate cart quantities against current stock
     * @returns {Array} Validated cart array
     */
    validateCartStock() {
        try {
            const cart = this.loadCart();
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
                this.saveCart(validatedCart);
                console.log('✅ Cart quantities validated and adjusted');
            }

            return validatedCart;
        } catch (error) {
            console.error('Error validating cart stock:', error);
            return this.loadCart();
        }
    }

    /**
>>>>>>> Stashed changes
     * Get cart summary with totals and counts
     */
    getCartSummary() {
        try {
            const cart = this.loadCart();
            
            const summary = {
                totalItems: 0,
                subtotal: 0,
                productCount: cart.length
            };

            cart.forEach(product => {
                const cantidad = product.cantidad || 1;
                const precio = Number(product.precio) || 0;
                
                summary.totalItems += cantidad;
                summary.subtotal += precio * cantidad;
            });

            return summary;
        } catch (error) {
            console.error('Error calculating cart summary:', error);
            return {
                totalItems: 0,
                subtotal: 0,
                productCount: 0
            };
        }
    }

    /**
     * Get product count for cart badge
     */
    getProductCount() {
        try {
            const cart = this.loadCart();
            return cart.reduce((total, product) => total + (product.cantidad || 1), 0);
        } catch (error) {
            console.error('Error getting product count:', error);
            return 0;
        }
    }

    /**
     * Check if cart is empty
     */
    isEmpty() {
        try {
            const cart = this.loadCart();
            return cart.length === 0;
        } catch (error) {
            console.error('Error checking if cart is empty:', error);
            return true;
        }
    }

    /**
     * Get formatted cart for WhatsApp message
     */
    getWhatsAppMessage() {
        try {
            const cart = this.loadCart();
            
            if (cart.length === 0) {
                return '';
            }

            let message = "Hola! Quería consultar sobre:\n\n";
            
            cart.forEach((product) => {
                const cantidad = product.cantidad || 1;
                const precio = Number(product.precio) || 0;
                const subtotal = precio * cantidad;
                
                message += `- Producto: ${product.titulo}\n`;
                message += `- Cantidad: ${cantidad}\n`;
                message += `- Precio unitario: $${precio.toLocaleString()}\n`;
                message += `- Subtotal: $${subtotal.toLocaleString()}\n`;
                
                if (product.genero) {
                    message += `- Género: ${product.genero}\n`;
                }
                
                // Prioritize selected sizes over available sizes
                if (product.tallesSeleccionados && product.tallesSeleccionados.length > 0) {
                    message += `- Talles seleccionados: ${product.tallesSeleccionados.join(', ')}\n`;
                } else if (product.talles && product.talles.length > 0 && !product.talles.includes('No')) {
                    message += `- Talles disponibles: ${product.talles.join(', ')}\n`;
                    message += `- ⚠️ Ningún talle seleccionado\n`;
                }
                
                if (product.color) {
                    message += `- Color: ${product.color}\n`;
                }
                
                message += '\n';
            });

            const summary = this.getCartSummary();
            message += `Total de productos: ${summary.totalItems}\n`;
            message += `Total: $${summary.subtotal.toLocaleString()}`;

            return message;
        } catch (error) {
            console.error('Error generating WhatsApp message:', error);
            return '';
        }
    }
}

// Create global instance
try {
    console.log('🔄 Creating CartDataManager...');
    window.cartManager = new CartDataManager();
    console.log('✅ CartDataManager created successfully:', window.cartManager);
    
    // Test basic functionality immediately
    try {
        const testLoad = window.cartManager.loadCart();
        console.log('✅ Initial cart load test successful:', testLoad);
    } catch (testError) {
        console.error('❌ Initial cart load test failed:', testError);
    }
    
} catch (error) {
    console.error('❌ Error creating CartDataManager:', error);
    console.error('Error details:', error.stack);
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CartDataManager;
}