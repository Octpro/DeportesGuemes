/**
 * End-to-End Tests for Deportes Güemes Store
 * Tests critical user workflows and system integration
 */

class E2ETestSuite {
    constructor() {
        this.testResults = [];
        this.currentTest = null;
        this.setupTestEnvironment();
    }

    setupTestEnvironment() {
        // Create test data backup
        this.originalProducts = JSON.parse(localStorage.getItem('productos') || '[]');
        this.originalCart = JSON.parse(localStorage.getItem('cart') || '[]');
        
        // Setup test products
        this.testProducts = [
            {
                id: 'test-001',
                title: 'Test Remera Deportiva',
                price: 2500,
                category: 'Remeras',
                discipline: 'Running',
                gender: 'Unisex',
                stock: 10,
                images: ['test-image.jpg'],
                variants: [
                    { size: 'M', color: 'Azul', stock: 5 },
                    { size: 'L', color: 'Rojo', stock: 5 }
                ]
            },
            {
                id: 'test-002',
                title: 'Test Pantalón Deportivo',
                price: 4500,
                category: 'Pantalones',
                discipline: 'Futbol',
                gender: 'Masculino',
                stock: 8,
                images: ['test-image2.jpg']
            }
        ];
    }

    async runAllTests() {
        console.log('🚀 Starting E2E Test Suite...');
        
        try {
            await this.testProductBrowsing();
            await this.testSearchAndFiltering();
            await this.testShoppingCartWorkflow();
            await this.testMobileResponsiveness();
            await this.testPerformanceMetrics();
            await this.testAccessibility();
            await this.testDataSynchronization();
            
            this.generateTestReport();
        } catch (error) {
            console.error('❌ Test suite failed:', error);
        } finally {
            this.cleanupTestEnvironment();
        }
    }

    async testProductBrowsing() {
        this.startTest('Product Browsing Workflow');
        
        try {
            // Test 1: Load products
            await this.loadTestProducts();
            this.assert(document.querySelectorAll('.product-card').length > 0, 'Products should be displayed');
            
            // Test 2: Product card interactions
            const firstProduct = document.querySelector('.product-card');
            this.assert(firstProduct !== null, 'First product card should exist');
            
            // Test 3: Product details modal
            const detailsBtn = firstProduct.querySelector('.product-details-btn');
            if (detailsBtn) {
                detailsBtn.click();
                await this.wait(500);
                this.assert(document.querySelector('.product-modal'), 'Product modal should open');
            }
            
            this.passTest('Product browsing works correctly');
        } catch (error) {
            this.failTest('Product browsing failed: ' + error.message);
        }
    }

    async testSearchAndFiltering() {
        this.startTest('Search and Filtering Workflow');
        
        try {
            // Test search functionality
            const searchInput = document.querySelector('#search-input');
            if (searchInput) {
                searchInput.value = 'remera';
                searchInput.dispatchEvent(new Event('input'));
                await this.wait(300);
                
                const visibleProducts = document.querySelectorAll('.product-card:not([style*="display: none"])');
                this.assert(visibleProducts.length > 0, 'Search should return results');
            }
            
            // Test category filtering
            const categoryFilter = document.querySelector('#category-filter');
            if (categoryFilter) {
                categoryFilter.value = 'Remeras';
                categoryFilter.dispatchEvent(new Event('change'));
                await this.wait(300);
                
                const filteredProducts = document.querySelectorAll('.product-card:not([style*="display: none"])');
                this.assert(filteredProducts.length > 0, 'Category filter should work');
            }
            
            // Test price range filter
            const priceSlider = document.querySelector('#price-range');
            if (priceSlider) {
                priceSlider.value = 3000;
                priceSlider.dispatchEvent(new Event('input'));
                await this.wait(300);
            }
            
            this.passTest('Search and filtering works correctly');
        } catch (error) {
            this.failTest('Search and filtering failed: ' + error.message);
        }
    }

    async testShoppingCartWorkflow() {
        this.startTest('Shopping Cart Workflow');
        
        try {
            // Clear cart first
            localStorage.removeItem('cart');
            
            // Test 1: Add product to cart
            const addToCartBtn = document.querySelector('.add-to-cart-btn');
            if (addToCartBtn) {
                addToCartBtn.click();
                await this.wait(500);
                
                const cart = JSON.parse(localStorage.getItem('cart') || '[]');
                this.assert(cart.length > 0, 'Product should be added to cart');
            }
            
            // Test 2: Cart persistence
            const cartBefore = JSON.parse(localStorage.getItem('cart') || '[]');
            window.location.reload();
            await this.wait(1000);
            const cartAfter = JSON.parse(localStorage.getItem('cart') || '[]');
            this.assert(cartBefore.length === cartAfter.length, 'Cart should persist after reload');
            
            // Test 3: Cart quantity updates
            if (window.updateCartQuantity) {
                const initialQuantity = cartAfter[0]?.quantity || 1;
                window.updateCartQuantity(cartAfter[0]?.id, initialQuantity + 1);
                const updatedCart = JSON.parse(localStorage.getItem('cart') || '[]');
                this.assert(updatedCart[0]?.quantity === initialQuantity + 1, 'Cart quantity should update');
            }
            
            this.passTest('Shopping cart workflow works correctly');
        } catch (error) {
            this.failTest('Shopping cart workflow failed: ' + error.message);
        }
    }

    async testMobileResponsiveness() {
        this.startTest('Mobile Responsiveness');
        
        try {
            // Simulate mobile viewport
            const originalWidth = window.innerWidth;
            Object.defineProperty(window, 'innerWidth', { value: 375, writable: true });
            window.dispatchEvent(new Event('resize'));
            await this.wait(300);
            
            // Test mobile navigation
            const mobileMenu = document.querySelector('.mobile-menu-toggle');
            if (mobileMenu) {
                this.assert(window.getComputedStyle(mobileMenu).display !== 'none', 'Mobile menu should be visible');
            }
            
            // Test responsive grid
            const productGrid = document.querySelector('.products-grid');
            if (productGrid) {
                const gridColumns = window.getComputedStyle(productGrid).gridTemplateColumns;
                this.assert(gridColumns.includes('1fr') || gridColumns.includes('repeat(1'), 'Mobile should show single column');
            }
            
            // Test touch interactions
            const touchElements = document.querySelectorAll('.touch-target');
            touchElements.forEach(element => {
                const rect = element.getBoundingClientRect();
                this.assert(rect.height >= 44, 'Touch targets should be at least 44px high');
            });
            
            // Restore original viewport
            Object.defineProperty(window, 'innerWidth', { value: originalWidth, writable: true });
            window.dispatchEvent(new Event('resize'));
            
            this.passTest('Mobile responsiveness works correctly');
        } catch (error) {
            this.failTest('Mobile responsiveness failed: ' + error.message);
        }
    }

    async testPerformanceMetrics() {
        this.startTest('Performance Metrics');
        
        try {
            // Test page load performance
            const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
            this.assert(loadTime < 3000, `Page load time should be under 3s (actual: ${loadTime}ms)`);
            
            // Test search performance
            const searchStart = performance.now();
            const searchInput = document.querySelector('#search-input');
            if (searchInput) {
                searchInput.value = 'test';
                searchInput.dispatchEvent(new Event('input'));
                await this.wait(100);
            }
            const searchTime = performance.now() - searchStart;
            this.assert(searchTime < 500, `Search should complete in under 500ms (actual: ${searchTime}ms)`);
            
            // Test image loading performance
            const images = document.querySelectorAll('img[loading="lazy"]');
            this.assert(images.length > 0, 'Lazy loading should be implemented for images');
            
            // Test cache performance
            if (window.CacheManager) {
                const cacheStart = performance.now();
                await window.CacheManager.getCachedProducts();
                const cacheTime = performance.now() - cacheStart;
                this.assert(cacheTime < 100, `Cache retrieval should be fast (actual: ${cacheTime}ms)`);
            }
            
            this.passTest('Performance metrics are within acceptable ranges');
        } catch (error) {
            this.failTest('Performance metrics failed: ' + error.message);
        }
    }

    async testAccessibility() {
        this.startTest('Accessibility Compliance');
        
        try {
            // Test ARIA labels
            const interactiveElements = document.querySelectorAll('button, input, select, a');
            let missingLabels = 0;
            interactiveElements.forEach(element => {
                if (!element.getAttribute('aria-label') && !element.getAttribute('aria-labelledby') && !element.textContent.trim()) {
                    missingLabels++;
                }
            });
            this.assert(missingLabels === 0, `All interactive elements should have labels (${missingLabels} missing)`);
            
            // Test keyboard navigation
            const focusableElements = document.querySelectorAll('button:not([disabled]), input:not([disabled]), select:not([disabled]), a[href]');
            this.assert(focusableElements.length > 0, 'Page should have focusable elements');
            
            // Test color contrast (basic check)
            const buttons = document.querySelectorAll('button');
            buttons.forEach(button => {
                const styles = window.getComputedStyle(button);
                this.assert(styles.backgroundColor !== styles.color, 'Button should have contrasting colors');
            });
            
            // Test alt text for images
            const images = document.querySelectorAll('img');
            let missingAlt = 0;
            images.forEach(img => {
                if (!img.getAttribute('alt')) {
                    missingAlt++;
                }
            });
            this.assert(missingAlt === 0, `All images should have alt text (${missingAlt} missing)`);
            
            this.passTest('Accessibility compliance checks passed');
        } catch (error) {
            this.failTest('Accessibility compliance failed: ' + error.message);
        }
    }

    async testDataSynchronization() {
        this.startTest('Data Synchronization');
        
        try {
            // Test cache synchronization
            if (window.CacheManager) {
                const testData = { test: 'data', timestamp: Date.now() };
                window.CacheManager.cacheProducts(testData);
                const retrieved = window.CacheManager.getCachedProducts();
                this.assert(JSON.stringify(retrieved) === JSON.stringify(testData), 'Cache should store and retrieve data correctly');
            }
            
            // Test localStorage synchronization
            const testCart = [{ id: 'sync-test', quantity: 1 }];
            localStorage.setItem('cart', JSON.stringify(testCart));
            const retrievedCart = JSON.parse(localStorage.getItem('cart'));
            this.assert(JSON.stringify(retrievedCart) === JSON.stringify(testCart), 'localStorage should sync correctly');
            
            // Test cross-tab synchronization
            window.dispatchEvent(new StorageEvent('storage', {
                key: 'cart',
                newValue: JSON.stringify(testCart),
                oldValue: '[]'
            }));
            await this.wait(100);
            
            this.passTest('Data synchronization works correctly');
        } catch (error) {
            this.failTest('Data synchronization failed: ' + error.message);
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

    async loadTestProducts() {
        // Simulate loading test products
        localStorage.setItem('productos', JSON.stringify(this.testProducts));
        if (window.loadProducts) {
            await window.loadProducts();
        }
    }

    generateTestReport() {
        const passed = this.testResults.filter(r => r.status === 'PASS').length;
        const failed = this.testResults.filter(r => r.status === 'FAIL').length;
        const totalDuration = this.testResults.reduce((sum, r) => sum + r.duration, 0);
        
        console.log('\n📊 Test Report:');
        console.log(`Total Tests: ${this.testResults.length}`);
        console.log(`Passed: ${passed}`);
        console.log(`Failed: ${failed}`);
        console.log(`Total Duration: ${totalDuration}ms`);
        console.log(`Success Rate: ${((passed / this.testResults.length) * 100).toFixed(1)}%`);
        
        // Store results for later analysis
        localStorage.setItem('e2e-test-results', JSON.stringify({
            timestamp: new Date().toISOString(),
            results: this.testResults,
            summary: { passed, failed, totalDuration }
        }));
    }

    cleanupTestEnvironment() {
        // Restore original data
        if (this.originalProducts.length > 0) {
            localStorage.setItem('productos', JSON.stringify(this.originalProducts));
        }
        if (this.originalCart.length > 0) {
            localStorage.setItem('cart', JSON.stringify(this.originalCart));
        }
        
        // Clean up test data
        localStorage.removeItem('test-data');
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = E2ETestSuite;
}

// Auto-run tests if this script is loaded directly
if (typeof window !== 'undefined' && window.location.search.includes('run-e2e-tests')) {
    document.addEventListener('DOMContentLoaded', () => {
        const testSuite = new E2ETestSuite();
        testSuite.runAllTests();
    });
}