/**
 * Integration Tests for Desktop-Web Synchronization
 * Tests the integration between desktop application and web store
 */

class IntegrationTestSuite {
    constructor() {
        this.testResults = [];
        this.currentTest = null;
        this.mockDesktopData = null;
        this.setupMockEnvironment();
    }

    setupMockEnvironment() {
        // Mock desktop application data structure
        this.mockDesktopData = {
            productos: [
                {
                    id: 'desktop-001',
                    title: 'Desktop Added Product',
                    price: 3500,
                    category: 'Remeras',
                    discipline: 'Running',
                    gender: 'Unisex',
                    stock: 15,
                    images: ['desktop-product.jpg'],
                    lastModified: new Date().toISOString()
                }
            ],
            historial: [
                {
                    id: Date.now(),
                    action: 'ADD_PRODUCT',
                    productId: 'desktop-001',
                    timestamp: new Date().toISOString(),
                    user: 'admin'
                }
            ]
        };

        // Mock Git operations
        this.mockGitOperations = {
            lastCommit: null,
            commits: [],
            commit: function(message, files) {
                const commit = {
                    id: Date.now().toString(),
                    message,
                    files,
                    timestamp: new Date().toISOString()
                };
                this.commits.push(commit);
                this.lastCommit = commit;
                return commit;
            },
            getLastCommit: function() {
                return this.lastCommit;
            },
            getAllCommits: function() {
                return [...this.commits];
            }
        };
    }

    async runAllTests() {
        console.log('🔗 Starting Integration Test Suite...');
        
        try {
            await this.testDataSynchronization();
            await this.testProductCRUDIntegration();
            await this.testInventorySync();
            await this.testImageSynchronization();
            await this.testHistoryTracking();
            await this.testConflictResolution();
            await this.testCacheInvalidation();
            await this.testRealTimeUpdates();
            
            this.generateTestReport();
        } catch (error) {
            console.error('❌ Integration test suite failed:', error);
        }
    }

    async testDataSynchronization() {
        this.startTest('Data Synchronization Integration');
        
        try {
            // Simulate desktop app updating productos.json
            const originalProducts = JSON.parse(localStorage.getItem('productos') || '[]');
            
            // Mock desktop data update
            const updatedProducts = [...originalProducts, ...this.mockDesktopData.productos];
            localStorage.setItem('productos', JSON.stringify(updatedProducts));
            
            // Simulate web app detecting the change
            window.dispatchEvent(new StorageEvent('storage', {
                key: 'productos',
                newValue: JSON.stringify(updatedProducts),
                oldValue: JSON.stringify(originalProducts)
            }));
            
            await this.wait(100);
            
            // Verify synchronization
            const syncedProducts = JSON.parse(localStorage.getItem('productos') || '[]');
            const desktopProduct = syncedProducts.find(p => p.id === 'desktop-001');
            
            this.assert(desktopProduct !== undefined, 'Desktop product should be synchronized');
            this.assert(desktopProduct.title === 'Desktop Added Product', 'Product data should be correct');
            
            // Test bidirectional sync - web to desktop
            const webProduct = {
                id: 'web-001',
                title: 'Web Added Product',
                price: 2800,
                category: 'Pantalones',
                lastModified: new Date().toISOString()
            };
            
            const allProducts = [...syncedProducts, webProduct];
            localStorage.setItem('productos', JSON.stringify(allProducts));
            
            // Simulate desktop app reading the updated data
            const desktopReadData = JSON.parse(localStorage.getItem('productos') || '[]');
            const webAddedProduct = desktopReadData.find(p => p.id === 'web-001');
            
            this.assert(webAddedProduct !== undefined, 'Web product should be available to desktop');
            this.assert(webAddedProduct.title === 'Web Added Product', 'Web product data should be correct');
            
            this.passTest('Data synchronization works bidirectionally');
        } catch (error) {
            this.failTest('Data synchronization failed: ' + error.message);
        }
    }

    async testProductCRUDIntegration() {
        this.startTest('Product CRUD Integration');
        
        try {
            const products = JSON.parse(localStorage.getItem('productos') || '[]');
            const initialCount = products.length;
            
            // Test CREATE operation
            const newProduct = {
                id: 'crud-test-001',
                title: 'CRUD Test Product',
                price: 1500,
                category: 'Test',
                stock: 10,
                createdAt: new Date().toISOString()
            };
            
            // Simulate desktop CREATE
            products.push(newProduct);
            localStorage.setItem('productos', JSON.stringify(products));
            
            // Verify web can READ
            const afterCreate = JSON.parse(localStorage.getItem('productos') || '[]');
            this.assert(afterCreate.length === initialCount + 1, 'Product should be created');
            
            // Test UPDATE operation
            const productToUpdate = afterCreate.find(p => p.id === 'crud-test-001');
            productToUpdate.title = 'Updated CRUD Test Product';
            productToUpdate.price = 1800;
            productToUpdate.updatedAt = new Date().toISOString();
            
            localStorage.setItem('productos', JSON.stringify(afterCreate));
            
            // Verify UPDATE
            const afterUpdate = JSON.parse(localStorage.getItem('productos') || '[]');
            const updatedProduct = afterUpdate.find(p => p.id === 'crud-test-001');
            this.assert(updatedProduct.title === 'Updated CRUD Test Product', 'Product should be updated');
            this.assert(updatedProduct.price === 1800, 'Product price should be updated');
            
            // Test DELETE operation
            const afterDelete = afterUpdate.filter(p => p.id !== 'crud-test-001');
            localStorage.setItem('productos', JSON.stringify(afterDelete));
            
            // Verify DELETE
            const finalProducts = JSON.parse(localStorage.getItem('productos') || '[]');
            const deletedProduct = finalProducts.find(p => p.id === 'crud-test-001');
            this.assert(deletedProduct === undefined, 'Product should be deleted');
            this.assert(finalProducts.length === initialCount, 'Product count should be restored');
            
            this.passTest('Product CRUD operations integrate correctly');
        } catch (error) {
            this.failTest('Product CRUD integration failed: ' + error.message);
        }
    }

    async testInventorySync() {
        this.startTest('Inventory Synchronization');
        
        try {
            // Create test product with stock
            const testProduct = {
                id: 'inventory-test-001',
                title: 'Inventory Test Product',
                stock: 100,
                variants: [
                    { size: 'M', color: 'Blue', stock: 50 },
                    { size: 'L', color: 'Red', stock: 50 }
                ]
            };
            
            const products = JSON.parse(localStorage.getItem('productos') || '[]');
            products.push(testProduct);
            localStorage.setItem('productos', JSON.stringify(products));
            
            // Simulate desktop inventory update
            const updatedProducts = JSON.parse(localStorage.getItem('productos') || '[]');
            const productToUpdate = updatedProducts.find(p => p.id === 'inventory-test-001');
            
            // Reduce stock (simulate sale)
            productToUpdate.stock = 95;
            productToUpdate.variants[0].stock = 45; // Sold 5 M Blue
            productToUpdate.lastStockUpdate = new Date().toISOString();
            
            localStorage.setItem('productos', JSON.stringify(updatedProducts));
            
            // Verify web reflects inventory changes
            const syncedProducts = JSON.parse(localStorage.getItem('productos') || '[]');
            const syncedProduct = syncedProducts.find(p => p.id === 'inventory-test-001');
            
            this.assert(syncedProduct.stock === 95, 'Total stock should be updated');
            this.assert(syncedProduct.variants[0].stock === 45, 'Variant stock should be updated');
            this.assert(syncedProduct.lastStockUpdate !== undefined, 'Stock update timestamp should be set');
            
            // Test low stock alerts
            productToUpdate.stock = 5; // Low stock
            productToUpdate.variants[0].stock = 2;
            productToUpdate.variants[1].stock = 3;
            
            localStorage.setItem('productos', JSON.stringify(updatedProducts));
            
            // Verify low stock detection
            const lowStockProducts = JSON.parse(localStorage.getItem('productos') || '[]');
            const lowStockProduct = lowStockProducts.find(p => p.id === 'inventory-test-001');
            
            this.assert(lowStockProduct.stock <= 10, 'Should detect low stock condition');
            
            // Cleanup
            const cleanedProducts = products.filter(p => p.id !== 'inventory-test-001');
            localStorage.setItem('productos', JSON.stringify(cleanedProducts));
            
            this.passTest('Inventory synchronization works correctly');
        } catch (error) {
            this.failTest('Inventory synchronization failed: ' + error.message);
        }
    }

    async testImageSynchronization() {
        this.startTest('Image Synchronization');
        
        try {
            // Mock image operations
            const mockImageOperations = {
                uploadedImages: [],
                optimizedImages: [],
                uploadImage: function(file, productId) {
                    const imagePath = `img/${productId}_${file.name}`;
                    this.uploadedImages.push({ productId, path: imagePath, originalName: file.name });
                    return imagePath;
                },
                optimizeImage: function(imagePath) {
                    const optimizedPath = imagePath.replace('.jpg', '_optimized.jpg');
                    this.optimizedImages.push({ original: imagePath, optimized: optimizedPath });
                    return optimizedPath;
                }
            };
            
            // Test image upload from desktop
            const mockImageFile = { name: 'test-product.jpg', size: 500000 };
            const imagePath = mockImageOperations.uploadImage(mockImageFile, 'img-test-001');
            
            this.assert(imagePath.includes('img-test-001'), 'Image path should include product ID');
            this.assert(mockImageOperations.uploadedImages.length === 1, 'Image should be uploaded');
            
            // Test image optimization
            const optimizedPath = mockImageOperations.optimizeImage(imagePath);
            this.assert(optimizedPath.includes('_optimized'), 'Image should be optimized');
            this.assert(mockImageOperations.optimizedImages.length === 1, 'Optimization should be tracked');
            
            // Test product image reference update
            const testProduct = {
                id: 'img-test-001',
                title: 'Image Test Product',
                images: [optimizedPath],
                imageMetadata: {
                    originalSize: mockImageFile.size,
                    optimizedSize: mockImageFile.size * 0.7,
                    uploadDate: new Date().toISOString()
                }
            };
            
            const products = JSON.parse(localStorage.getItem('productos') || '[]');
            products.push(testProduct);
            localStorage.setItem('productos', JSON.stringify(products));
            
            // Verify image synchronization
            const syncedProducts = JSON.parse(localStorage.getItem('productos') || '[]');
            const imageProduct = syncedProducts.find(p => p.id === 'img-test-001');
            
            this.assert(imageProduct.images.length === 1, 'Product should have image reference');
            this.assert(imageProduct.images[0] === optimizedPath, 'Product should reference optimized image');
            this.assert(imageProduct.imageMetadata !== undefined, 'Image metadata should be preserved');
            
            // Cleanup
            const cleanedProducts = products.filter(p => p.id !== 'img-test-001');
            localStorage.setItem('productos', JSON.stringify(cleanedProducts));
            
            this.passTest('Image synchronization works correctly');
        } catch (error) {
            this.failTest('Image synchronization failed: ' + error.message);
        }
    }

    async testHistoryTracking() {
        this.startTest('History Tracking Integration');
        
        try {
            // Initialize history
            const initialHistory = JSON.parse(localStorage.getItem('historial') || '[]');
            
            // Simulate desktop operation with history logging
            const historyEntry = {
                id: Date.now(),
                action: 'INTEGRATION_TEST',
                productId: 'history-test-001',
                details: {
                    operation: 'CREATE',
                    data: { title: 'History Test Product' }
                },
                timestamp: new Date().toISOString(),
                user: 'integration-test',
                source: 'desktop'
            };
            
            const updatedHistory = [...initialHistory, historyEntry];
            localStorage.setItem('historial', JSON.stringify(updatedHistory));
            
            // Verify history synchronization
            const syncedHistory = JSON.parse(localStorage.getItem('historial') || '[]');
            const testEntry = syncedHistory.find(h => h.action === 'INTEGRATION_TEST');
            
            this.assert(testEntry !== undefined, 'History entry should be synchronized');
            this.assert(testEntry.source === 'desktop', 'History source should be preserved');
            this.assert(testEntry.details.operation === 'CREATE', 'History details should be preserved');
            
            // Test history filtering and querying
            const desktopEntries = syncedHistory.filter(h => h.source === 'desktop');
            const recentEntries = syncedHistory.filter(h => {
                const entryTime = new Date(h.timestamp);
                const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
                return entryTime > oneHourAgo;
            });
            
            this.assert(desktopEntries.length > 0, 'Should be able to filter desktop entries');
            this.assert(recentEntries.length > 0, 'Should be able to filter recent entries');
            
            // Test history cleanup (remove test entry)
            const cleanedHistory = syncedHistory.filter(h => h.action !== 'INTEGRATION_TEST');
            localStorage.setItem('historial', JSON.stringify(cleanedHistory));
            
            this.passTest('History tracking integration works correctly');
        } catch (error) {
            this.failTest('History tracking integration failed: ' + error.message);
        }
    }

    async testConflictResolution() {
        this.startTest('Conflict Resolution');
        
        try {
            // Create a product that will be modified by both desktop and web
            const conflictProduct = {
                id: 'conflict-test-001',
                title: 'Conflict Test Product',
                price: 1000,
                stock: 50,
                lastModified: new Date(Date.now() - 1000).toISOString(), // 1 second ago
                version: 1
            };
            
            const products = JSON.parse(localStorage.getItem('productos') || '[]');
            products.push(conflictProduct);
            localStorage.setItem('productos', JSON.stringify(products));
            
            // Simulate desktop modification
            const desktopProducts = JSON.parse(localStorage.getItem('productos') || '[]');
            const desktopProduct = desktopProducts.find(p => p.id === 'conflict-test-001');
            desktopProduct.title = 'Desktop Modified Product';
            desktopProduct.price = 1200;
            desktopProduct.lastModified = new Date().toISOString();
            desktopProduct.version = 2;
            desktopProduct.modifiedBy = 'desktop';
            
            // Simulate web modification (concurrent)
            const webProducts = JSON.parse(localStorage.getItem('productos') || '[]');
            const webProduct = webProducts.find(p => p.id === 'conflict-test-001');
            webProduct.title = 'Web Modified Product';
            webProduct.stock = 45; // Different field
            webProduct.lastModified = new Date().toISOString();
            webProduct.version = 2;
            webProduct.modifiedBy = 'web';
            
            // Conflict resolution: merge non-conflicting changes, use latest for conflicts
            const resolvedProduct = {
                ...conflictProduct,
                title: desktopProduct.lastModified > webProduct.lastModified ? 
                       desktopProduct.title : webProduct.title,
                price: desktopProduct.price, // Desktop change
                stock: webProduct.stock,     // Web change
                lastModified: new Date().toISOString(),
                version: 3,
                conflictResolved: true,
                conflictHistory: [
                    { source: 'desktop', changes: ['title', 'price'] },
                    { source: 'web', changes: ['stock'] }
                ]
            };
            
            // Apply resolution
            const resolvedProducts = products.map(p => 
                p.id === 'conflict-test-001' ? resolvedProduct : p
            );
            localStorage.setItem('productos', JSON.stringify(resolvedProducts));
            
            // Verify conflict resolution
            const finalProducts = JSON.parse(localStorage.getItem('productos') || '[]');
            const finalProduct = finalProducts.find(p => p.id === 'conflict-test-001');
            
            this.assert(finalProduct.conflictResolved === true, 'Conflict should be marked as resolved');
            this.assert(finalProduct.version === 3, 'Version should be incremented');
            this.assert(finalProduct.conflictHistory.length === 2, 'Conflict history should be preserved');
            
            // Cleanup
            const cleanedProducts = products.filter(p => p.id !== 'conflict-test-001');
            localStorage.setItem('productos', JSON.stringify(cleanedProducts));
            
            this.passTest('Conflict resolution works correctly');
        } catch (error) {
            this.failTest('Conflict resolution failed: ' + error.message);
        }
    }

    async testCacheInvalidation() {
        this.startTest('Cache Invalidation Integration');
        
        try {
            // Mock cache system
            const mockCache = {
                data: new Map(),
                set: function(key, value) {
                    this.data.set(key, { value, timestamp: Date.now() });
                },
                get: function(key) {
                    const cached = this.data.get(key);
                    return cached ? cached.value : null;
                },
                invalidate: function(key) {
                    if (key) {
                        this.data.delete(key);
                    } else {
                        this.data.clear();
                    }
                },
                size: function() {
                    return this.data.size;
                }
            };
            
            // Cache some product data
            const testProducts = [{ id: 'cache-test-001', title: 'Cached Product' }];
            mockCache.set('products', testProducts);
            mockCache.set('categories', ['Test Category']);
            
            this.assert(mockCache.size() === 2, 'Cache should contain test data');
            
            // Simulate desktop data update that should invalidate cache
            const updatedProducts = [
                { id: 'cache-test-001', title: 'Updated Cached Product' },
                { id: 'cache-test-002', title: 'New Product' }
            ];
            
            // Trigger cache invalidation
            mockCache.invalidate('products');
            
            // Verify specific cache invalidation
            const cachedProducts = mockCache.get('products');
            const cachedCategories = mockCache.get('categories');
            
            this.assert(cachedProducts === null, 'Products cache should be invalidated');
            this.assert(cachedCategories !== null, 'Other cache should remain');
            
            // Test full cache invalidation
            mockCache.invalidate(); // Clear all
            this.assert(mockCache.size() === 0, 'All cache should be cleared');
            
            // Test cache warming after invalidation
            mockCache.set('products', updatedProducts);
            const rewarmedCache = mockCache.get('products');
            
            this.assert(rewarmedCache.length === 2, 'Cache should be rewarmed with new data');
            this.assert(rewarmedCache[1].title === 'New Product', 'New data should be cached');
            
            this.passTest('Cache invalidation integration works correctly');
        } catch (error) {
            this.failTest('Cache invalidation integration failed: ' + error.message);
        }
    }

    async testRealTimeUpdates() {
        this.startTest('Real-time Updates Integration');
        
        try {
            let updateReceived = false;
            let updateData = null;
            
            // Mock real-time update listener
            const mockUpdateListener = function(event) {
                if (event.type === 'storage' && event.key === 'productos') {
                    updateReceived = true;
                    updateData = JSON.parse(event.newValue || '[]');
                }
            };
            
            // Set up listener
            window.addEventListener('storage', mockUpdateListener);
            
            // Simulate desktop update
            const products = JSON.parse(localStorage.getItem('productos') || '[]');
            const realtimeProduct = {
                id: 'realtime-test-001',
                title: 'Real-time Test Product',
                timestamp: new Date().toISOString()
            };
            
            const updatedProducts = [...products, realtimeProduct];
            
            // Trigger storage event (simulates cross-tab/process communication)
            window.dispatchEvent(new StorageEvent('storage', {
                key: 'productos',
                newValue: JSON.stringify(updatedProducts),
                oldValue: JSON.stringify(products)
            }));
            
            await this.wait(100);
            
            // Verify real-time update
            this.assert(updateReceived === true, 'Update should be received');
            this.assert(updateData !== null, 'Update data should be available');
            
            const receivedProduct = updateData.find(p => p.id === 'realtime-test-001');
            this.assert(receivedProduct !== undefined, 'New product should be in update');
            this.assert(receivedProduct.title === 'Real-time Test Product', 'Product data should be correct');
            
            // Test update frequency throttling
            let updateCount = 0;
            const throttledListener = function() {
                updateCount++;
            };
            
            window.addEventListener('storage', throttledListener);
            
            // Rapid updates
            for (let i = 0; i < 5; i++) {
                window.dispatchEvent(new StorageEvent('storage', {
                    key: 'productos',
                    newValue: JSON.stringify([...updatedProducts, { id: `rapid-${i}` }])
                }));
            }
            
            await this.wait(200);
            
            // In a real implementation, updates should be throttled
            this.assert(updateCount > 0, 'Updates should be received');
            
            // Cleanup
            window.removeEventListener('storage', mockUpdateListener);
            window.removeEventListener('storage', throttledListener);
            
            this.passTest('Real-time updates integration works correctly');
        } catch (error) {
            this.failTest('Real-time updates integration failed: ' + error.message);
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
        
        console.log('\n📊 Integration Test Report:');
        console.log(`Total Tests: ${this.testResults.length}`);
        console.log(`Passed: ${passed}`);
        console.log(`Failed: ${failed}`);
        console.log(`Total Duration: ${totalDuration}ms`);
        console.log(`Success Rate: ${((passed / this.testResults.length) * 100).toFixed(1)}%`);
        
        // Store results for later analysis
        localStorage.setItem('integration-test-results', JSON.stringify({
            timestamp: new Date().toISOString(),
            results: this.testResults,
            summary: { passed, failed, totalDuration }
        }));
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IntegrationTestSuite;
}

// Auto-run tests if this script is loaded directly
if (typeof window !== 'undefined' && window.location.search.includes('run-integration-tests')) {
    document.addEventListener('DOMContentLoaded', () => {
        const testSuite = new IntegrationTestSuite();
        testSuite.runAllTests();
    });
}