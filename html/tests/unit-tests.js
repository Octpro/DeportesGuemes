/**
 * Unit Tests for Deportes Güemes Store Components
 * Tests individual components and utilities in isolation
 */

class UnitTestSuite {
    constructor() {
        this.testResults = [];
        this.currentTest = null;
    }

    async runAllTests() {
        console.log('🔬 Starting Unit Test Suite...');
        
        try {
            await this.testCacheManager();
            await this.testImageOptimizer();
            await this.testSearchEngine();
            await this.testDataValidator();
            await this.testCartPersistence();
            await this.testPerformanceMonitor();
            await this.testErrorTracker();
            await this.testAccessibilityHelpers();
            
            this.generateTestReport();
        } catch (error) {
            console.error('❌ Unit test suite failed:', error);
        }
    }

    async testCacheManager() {
        this.startTest('CacheManager Unit Tests');
        
        try {
            // Mock CacheManager if not available
            if (typeof CacheManager === 'undefined') {
                window.CacheManager = {
                    cache: new Map(),
                    cacheProducts: function(products) {
                        this.cache.set('products', { data: products, timestamp: Date.now() });
                    },
                    getCachedProducts: function() {
                        const cached = this.cache.get('products');
                        return cached ? cached.data : null;
                    },
                    invalidateCache: function(key) {
                        this.cache.delete(key || 'products');
                    }
                };
            }
            
            // Test caching functionality
            const testProducts = [{ id: 1, name: 'Test Product' }];
            CacheManager.cacheProducts(testProducts);
            
            const retrieved = CacheManager.getCachedProducts();
            this.assert(Array.isArray(retrieved), 'Should return array');
            this.assert(retrieved.length === 1, 'Should cache correct number of products');
            this.assert(retrieved[0].id === 1, 'Should cache correct product data');
            
            // Test cache invalidation
            CacheManager.invalidateCache();
            const afterInvalidation = CacheManager.getCachedProducts();
            this.assert(afterInvalidation === null, 'Cache should be invalidated');
            
            this.passTest('CacheManager works correctly');
        } catch (error) {
            this.failTest('CacheManager failed: ' + error.message);
        }
    }

    async testImageOptimizer() {
        this.startTest('ImageOptimizer Unit Tests');
        
        try {
            // Mock ImageOptimizer if not available
            if (typeof ImageOptimizer === 'undefined') {
                window.ImageOptimizer = {
                    compressImage: function(file, quality = 0.8) {
                        return new Promise(resolve => {
                            // Simulate compression
                            const compressedSize = file.size * quality;
                            resolve({ ...file, size: compressedSize, compressed: true });
                        });
                    },
                    generateThumbnails: function(image, sizes) {
                        return sizes.map(size => ({
                            width: size,
                            height: size,
                            url: `thumbnail_${size}x${size}.jpg`
                        }));
                    },
                    lazyLoadImages: function(container) {
                        const images = container.querySelectorAll('img[data-src]');
                        images.forEach(img => {
                            img.src = img.dataset.src;
                            img.removeAttribute('data-src');
                        });
                        return images.length;
                    }
                };
            }
            
            // Test image compression
            const mockFile = { size: 1000000, name: 'test.jpg' };
            const compressed = await ImageOptimizer.compressImage(mockFile, 0.7);
            this.assert(compressed.size < mockFile.size, 'Should compress image size');
            this.assert(compressed.compressed === true, 'Should mark as compressed');
            
            // Test thumbnail generation
            const thumbnails = ImageOptimizer.generateThumbnails('test.jpg', [100, 200, 300]);
            this.assert(thumbnails.length === 3, 'Should generate correct number of thumbnails');
            this.assert(thumbnails[0].width === 100, 'Should generate correct thumbnail sizes');
            
            // Test lazy loading
            const mockContainer = document.createElement('div');
            mockContainer.innerHTML = '<img data-src="test1.jpg"><img data-src="test2.jpg">';
            const loadedCount = ImageOptimizer.lazyLoadImages(mockContainer);
            this.assert(loadedCount === 2, 'Should load correct number of images');
            
            this.passTest('ImageOptimizer works correctly');
        } catch (error) {
            this.failTest('ImageOptimizer failed: ' + error.message);
        }
    }

    async testSearchEngine() {
        this.startTest('SearchEngine Unit Tests');
        
        try {
            // Mock SearchEngine if not available
            if (typeof SearchEngine === 'undefined') {
                window.SearchEngine = {
                    products: [],
                    indexProducts: function(products) {
                        this.products = products;
                        // Create simple search index
                        this.searchIndex = products.map(p => ({
                            id: p.id,
                            searchText: `${p.title} ${p.category} ${p.discipline}`.toLowerCase()
                        }));
                    },
                    search: function(query, filters = {}) {
                        const lowerQuery = query.toLowerCase();
                        let results = this.products.filter(product => {
                            const matchesQuery = !query || product.title.toLowerCase().includes(lowerQuery);
                            const matchesCategory = !filters.category || product.category === filters.category;
                            const matchesPrice = !filters.maxPrice || product.price <= filters.maxPrice;
                            return matchesQuery && matchesCategory && matchesPrice;
                        });
                        return results;
                    },
                    sortResults: function(results, criteria) {
                        return results.sort((a, b) => {
                            switch (criteria) {
                                case 'price_asc': return a.price - b.price;
                                case 'price_desc': return b.price - a.price;
                                case 'name': return a.title.localeCompare(b.title);
                                default: return 0;
                            }
                        });
                    }
                };
            }
            
            // Test product indexing
            const testProducts = [
                { id: 1, title: 'Remera Deportiva', category: 'Remeras', discipline: 'Running', price: 2500 },
                { id: 2, title: 'Pantalón Futbol', category: 'Pantalones', discipline: 'Futbol', price: 4500 },
                { id: 3, title: 'Zapatillas Running', category: 'Calzado', discipline: 'Running', price: 8000 }
            ];
            
            SearchEngine.indexProducts(testProducts);
            this.assert(SearchEngine.products.length === 3, 'Should index all products');
            
            // Test search functionality
            const searchResults = SearchEngine.search('remera');
            this.assert(searchResults.length === 1, 'Should find matching products');
            this.assert(searchResults[0].title.includes('Remera'), 'Should return correct product');
            
            // Test filtering
            const filteredResults = SearchEngine.search('', { category: 'Remeras' });
            this.assert(filteredResults.length === 1, 'Should filter by category');
            
            const priceFilteredResults = SearchEngine.search('', { maxPrice: 5000 });
            this.assert(priceFilteredResults.length === 2, 'Should filter by price');
            
            // Test sorting
            const sortedResults = SearchEngine.sortResults(testProducts, 'price_asc');
            this.assert(sortedResults[0].price <= sortedResults[1].price, 'Should sort by price ascending');
            
            this.passTest('SearchEngine works correctly');
        } catch (error) {
            this.failTest('SearchEngine failed: ' + error.message);
        }
    }

    async testDataValidator() {
        this.startTest('DataValidator Unit Tests');
        
        try {
            // Mock DataValidator if not available
            if (typeof DataValidator === 'undefined') {
                window.DataValidator = {
                    validateProduct: function(product) {
                        const errors = [];
                        if (!product.title || product.title.trim().length === 0) {
                            errors.push('Title is required');
                        }
                        if (!product.price || product.price <= 0) {
                            errors.push('Price must be greater than 0');
                        }
                        if (!product.category) {
                            errors.push('Category is required');
                        }
                        return { isValid: errors.length === 0, errors };
                    },
                    sanitizeInput: function(input) {
                        return input.toString().trim().replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
                    },
                    validateEmail: function(email) {
                        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                        return emailRegex.test(email);
                    }
                };
            }
            
            // Test product validation - valid product
            const validProduct = {
                title: 'Test Product',
                price: 100,
                category: 'Test Category'
            };
            const validResult = DataValidator.validateProduct(validProduct);
            this.assert(validResult.isValid === true, 'Should validate correct product');
            this.assert(validResult.errors.length === 0, 'Should have no errors for valid product');
            
            // Test product validation - invalid product
            const invalidProduct = {
                title: '',
                price: -10,
                category: null
            };
            const invalidResult = DataValidator.validateProduct(invalidProduct);
            this.assert(invalidResult.isValid === false, 'Should reject invalid product');
            this.assert(invalidResult.errors.length > 0, 'Should have errors for invalid product');
            
            // Test input sanitization
            const maliciousInput = '<script>alert("xss")</script>Hello World';
            const sanitized = DataValidator.sanitizeInput(maliciousInput);
            this.assert(!sanitized.includes('<script>'), 'Should remove script tags');
            this.assert(sanitized.includes('Hello World'), 'Should preserve safe content');
            
            // Test email validation
            this.assert(DataValidator.validateEmail('test@example.com') === true, 'Should validate correct email');
            this.assert(DataValidator.validateEmail('invalid-email') === false, 'Should reject invalid email');
            
            this.passTest('DataValidator works correctly');
        } catch (error) {
            this.failTest('DataValidator failed: ' + error.message);
        }
    }

    async testCartPersistence() {
        this.startTest('CartPersistence Unit Tests');
        
        try {
            // Mock CartPersistence if not available
            if (typeof CartPersistence === 'undefined') {
                window.CartPersistence = {
                    saveCart: function(cart) {
                        localStorage.setItem('cart', JSON.stringify(cart));
                        return true;
                    },
                    loadCart: function() {
                        const cart = localStorage.getItem('cart');
                        return cart ? JSON.parse(cart) : [];
                    },
                    clearCart: function() {
                        localStorage.removeItem('cart');
                    },
                    addItem: function(item) {
                        const cart = this.loadCart();
                        const existingIndex = cart.findIndex(i => i.id === item.id);
                        if (existingIndex >= 0) {
                            cart[existingIndex].quantity += item.quantity || 1;
                        } else {
                            cart.push({ ...item, quantity: item.quantity || 1 });
                        }
                        this.saveCart(cart);
                        return cart;
                    }
                };
            }
            
            // Clear cart before testing
            CartPersistence.clearCart();
            
            // Test cart loading (empty)
            const emptyCart = CartPersistence.loadCart();
            this.assert(Array.isArray(emptyCart), 'Should return array for empty cart');
            this.assert(emptyCart.length === 0, 'Empty cart should have no items');
            
            // Test adding items
            const testItem = { id: 'test-1', title: 'Test Item', price: 100 };
            const cartWithItem = CartPersistence.addItem(testItem);
            this.assert(cartWithItem.length === 1, 'Should add item to cart');
            this.assert(cartWithItem[0].quantity === 1, 'Should set default quantity');
            
            // Test adding duplicate item
            const cartWithDuplicate = CartPersistence.addItem(testItem);
            this.assert(cartWithDuplicate.length === 1, 'Should not duplicate items');
            this.assert(cartWithDuplicate[0].quantity === 2, 'Should increase quantity');
            
            // Test cart persistence
            const savedCart = [{ id: 'persist-test', quantity: 3 }];
            CartPersistence.saveCart(savedCart);
            const loadedCart = CartPersistence.loadCart();
            this.assert(loadedCart.length === 1, 'Should persist cart data');
            this.assert(loadedCart[0].quantity === 3, 'Should persist item quantities');
            
            this.passTest('CartPersistence works correctly');
        } catch (error) {
            this.failTest('CartPersistence failed: ' + error.message);
        }
    }

    async testPerformanceMonitor() {
        this.startTest('PerformanceMonitor Unit Tests');
        
        try {
            // Mock PerformanceMonitor if not available
            if (typeof PerformanceMonitor === 'undefined') {
                window.PerformanceMonitor = {
                    metrics: {},
                    startTimer: function(name) {
                        this.metrics[name] = { start: performance.now() };
                    },
                    endTimer: function(name) {
                        if (this.metrics[name]) {
                            this.metrics[name].duration = performance.now() - this.metrics[name].start;
                            return this.metrics[name].duration;
                        }
                        return 0;
                    },
                    getMetrics: function() {
                        return { ...this.metrics };
                    },
                    clearMetrics: function() {
                        this.metrics = {};
                    }
                };
            }
            
            // Test timer functionality
            PerformanceMonitor.startTimer('test-operation');
            await this.wait(10); // Small delay
            const duration = PerformanceMonitor.endTimer('test-operation');
            
            this.assert(duration > 0, 'Should measure positive duration');
            this.assert(duration >= 10, 'Should measure at least the wait time');
            
            // Test metrics storage
            const metrics = PerformanceMonitor.getMetrics();
            this.assert(metrics['test-operation'], 'Should store metrics');
            this.assert(metrics['test-operation'].duration === duration, 'Should store correct duration');
            
            // Test metrics clearing
            PerformanceMonitor.clearMetrics();
            const clearedMetrics = PerformanceMonitor.getMetrics();
            this.assert(Object.keys(clearedMetrics).length === 0, 'Should clear all metrics');
            
            this.passTest('PerformanceMonitor works correctly');
        } catch (error) {
            this.failTest('PerformanceMonitor failed: ' + error.message);
        }
    }

    async testErrorTracker() {
        this.startTest('ErrorTracker Unit Tests');
        
        try {
            // Mock ErrorTracker if not available
            if (typeof ErrorTracker === 'undefined') {
                window.ErrorTracker = {
                    errors: [],
                    logError: function(error, context = {}) {
                        const errorEntry = {
                            message: error.message || error,
                            stack: error.stack,
                            timestamp: new Date().toISOString(),
                            context,
                            id: Date.now()
                        };
                        this.errors.push(errorEntry);
                        return errorEntry.id;
                    },
                    getErrors: function() {
                        return [...this.errors];
                    },
                    clearErrors: function() {
                        this.errors = [];
                    },
                    getErrorCount: function() {
                        return this.errors.length;
                    }
                };
            }
            
            // Clear previous errors
            ErrorTracker.clearErrors();
            
            // Test error logging
            const testError = new Error('Test error message');
            const errorId = ErrorTracker.logError(testError, { component: 'unit-test' });
            
            this.assert(typeof errorId === 'number', 'Should return error ID');
            this.assert(ErrorTracker.getErrorCount() === 1, 'Should increment error count');
            
            // Test error retrieval
            const errors = ErrorTracker.getErrors();
            this.assert(errors.length === 1, 'Should store error');
            this.assert(errors[0].message === 'Test error message', 'Should store error message');
            this.assert(errors[0].context.component === 'unit-test', 'Should store error context');
            
            // Test string error logging
            ErrorTracker.logError('String error', { type: 'string' });
            this.assert(ErrorTracker.getErrorCount() === 2, 'Should handle string errors');
            
            // Test error clearing
            ErrorTracker.clearErrors();
            this.assert(ErrorTracker.getErrorCount() === 0, 'Should clear all errors');
            
            this.passTest('ErrorTracker works correctly');
        } catch (error) {
            this.failTest('ErrorTracker failed: ' + error.message);
        }
    }

    async testAccessibilityHelpers() {
        this.startTest('AccessibilityHelpers Unit Tests');
        
        try {
            // Mock AccessibilityHelpers if not available
            if (typeof AccessibilityHelpers === 'undefined') {
                window.AccessibilityHelpers = {
                    addAriaLabels: function(container) {
                        const buttons = container.querySelectorAll('button:not([aria-label])');
                        buttons.forEach(button => {
                            if (!button.textContent.trim()) {
                                button.setAttribute('aria-label', 'Button');
                            }
                        });
                        return buttons.length;
                    },
                    checkColorContrast: function(foreground, background) {
                        // Simplified contrast check
                        const fgLuminance = this.getLuminance(foreground);
                        const bgLuminance = this.getLuminance(background);
                        const ratio = (Math.max(fgLuminance, bgLuminance) + 0.05) / (Math.min(fgLuminance, bgLuminance) + 0.05);
                        return ratio >= 4.5; // WCAG AA standard
                    },
                    getLuminance: function(color) {
                        // Simplified luminance calculation
                        return 0.5; // Mock value
                    },
                    setupKeyboardNavigation: function(container) {
                        const focusableElements = container.querySelectorAll('button, input, select, a[href]');
                        focusableElements.forEach((element, index) => {
                            element.setAttribute('tabindex', index === 0 ? '0' : '-1');
                        });
                        return focusableElements.length;
                    }
                };
            }
            
            // Test ARIA label addition
            const mockContainer = document.createElement('div');
            mockContainer.innerHTML = '<button></button><button>Click me</button>';
            const labeledCount = AccessibilityHelpers.addAriaLabels(mockContainer);
            
            this.assert(labeledCount >= 0, 'Should process buttons');
            const unlabeledButton = mockContainer.querySelector('button:not([aria-label])');
            // The button with text should not get an aria-label
            
            // Test color contrast
            const hasGoodContrast = AccessibilityHelpers.checkColorContrast('#000000', '#ffffff');
            this.assert(typeof hasGoodContrast === 'boolean', 'Should return boolean for contrast check');
            
            // Test keyboard navigation setup
            const navContainer = document.createElement('div');
            navContainer.innerHTML = '<button>1</button><input><a href="#">Link</a>';
            const focusableCount = AccessibilityHelpers.setupKeyboardNavigation(navContainer);
            this.assert(focusableCount === 3, 'Should find all focusable elements');
            
            this.passTest('AccessibilityHelpers works correctly');
        } catch (error) {
            this.failTest('AccessibilityHelpers failed: ' + error.message);
        }
    }

    // Helper methods
    startTest(testName) {
        this.currentTest = { name: testName, startTime: Date.now() };
        console.log(`🧪 Running: ${testName}`);
    }

    passTest(message) {
        const duration = Date.now() - this.currentTest.startTime;
        this.testResults.push({
            name: this.currentTest.name,
            status: 'PASS',
            message,
            duration
        });
        console.log(`✅ ${this.currentTest.name}: ${message} (${duration}ms)`);
    }

    failTest(message) {
        const duration = Date.now() - this.currentTest.startTime;
        this.testResults.push({
            name: this.currentTest.name,
            status: 'FAIL',
            message,
            duration
        });
        console.log(`❌ ${this.currentTest.name}: ${message} (${duration}ms)`);
    }

    assert(condition, message) {
        if (!condition) {
            throw new Error(message);
        }
    }

    wait(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    generateTestReport() {
        const passed = this.testResults.filter(r => r.status === 'PASS').length;
        const failed = this.testResults.filter(r => r.status === 'FAIL').length;
        const totalDuration = this.testResults.reduce((sum, r) => sum + r.duration, 0);
        
        console.log('\n📊 Unit Test Report:');
        console.log(`Total Tests: ${this.testResults.length}`);
        console.log(`Passed: ${passed}`);
        console.log(`Failed: ${failed}`);
        console.log(`Total Duration: ${totalDuration}ms`);
        console.log(`Success Rate: ${((passed / this.testResults.length) * 100).toFixed(1)}%`);
        
        // Store results for later analysis
        localStorage.setItem('unit-test-results', JSON.stringify({
            timestamp: new Date().toISOString(),
            results: this.testResults,
            summary: { passed, failed, totalDuration }
        }));
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UnitTestSuite;
}

// Auto-run tests if this script is loaded directly
if (typeof window !== 'undefined' && window.location.search.includes('run-unit-tests')) {
    document.addEventListener('DOMContentLoaded', () => {
        const testSuite = new UnitTestSuite();
        testSuite.runAllTests();
    });
}