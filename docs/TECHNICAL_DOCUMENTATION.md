# Deportes Güemes - Technical Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [System Components](#system-components)
3. [Data Flow](#data-flow)
4. [API Reference](#api-reference)
5. [Database Schema](#database-schema)
6. [Performance Optimization](#performance-optimization)
7. [Security Implementation](#security-implementation)
8. [Testing Framework](#testing-framework)
9. [Deployment Guide](#deployment-guide)
10. [Maintenance Procedures](#maintenance-procedures)
11. [Troubleshooting Guide](#troubleshooting-guide)

## Architecture Overview

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Desktop App   │    │   Git Repository │    │   Web Store     │
│   (Python/Tk)  │◄──►│   (JSON Data)    │◄──►│   (HTML/JS)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Local Storage  │    │  Version Control │    │ Browser Storage │
│   (JSON Files)  │    │   (Git History)  │    │  (localStorage) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack

#### Desktop Application
- **Framework**: Python 3.8+ with CustomTkinter
- **Image Processing**: PIL (Pillow)
- **Version Control**: GitPython
- **Data Format**: JSON
- **UI Library**: CustomTkinter (modern Tkinter)

#### Web Application
- **Frontend**: Vanilla HTML5, CSS3, JavaScript ES6+
- **Styling**: CSS Grid, Flexbox, Custom Properties
- **Icons**: Bootstrap Icons
- **Notifications**: Toastify.js
- **Modals**: SweetAlert2
- **Storage**: localStorage, sessionStorage

#### Data Layer
- **Primary Storage**: JSON files
- **Synchronization**: Git repository
- **Caching**: Browser localStorage
- **Backup**: Automated JSON backups

## System Components

### Desktop Application Components

#### Core Modules

**`customtk.py`** - Main application entry point
```python
class MainApplication:
    def __init__(self):
        self.setup_ui()
        self.load_data()
        self.setup_event_handlers()
    
    def setup_ui(self):
        # Initialize CustomTkinter interface
        
    def load_data(self):
        # Load products from JSON
        
    def setup_event_handlers(self):
        # Bind UI events to handlers
```

**`product_manager.py`** - Product management logic
```python
class ProductManager:
    def add_product(self, product_data):
        # Validate and add product
        
    def update_product(self, product_id, updates):
        # Update existing product
        
    def delete_product(self, product_id):
        # Remove product from catalog
```

**`data_synchronizer.py`** - Git synchronization
```python
class DataSynchronizer:
    def commit_changes(self, message):
        # Commit changes to Git
        
    def push_changes(self):
        # Push to remote repository
        
    def pull_changes(self):
        # Pull latest changes
```

#### UI Components

**Dialog Classes**
- `ProductDialog`: Add/edit product interface
- `InventoryDialog`: Stock management interface
- `SettingsDialog`: Application configuration
- `BackupDialog`: Backup management interface

### Web Application Components

#### JavaScript Modules

**`main.js`** - Core application logic
```javascript
class StoreApp {
    constructor() {
        this.products = [];
        this.cart = [];
        this.filters = {};
        this.init();
    }
    
    async init() {
        await this.loadProducts();
        this.setupEventListeners();
        this.renderProducts();
    }
}
```

**`cache-manager.js`** - Caching system
```javascript
class CacheManager {
    static cacheProducts(products) {
        // Cache product data with TTL
    }
    
    static getCachedProducts() {
        // Retrieve cached products
    }
    
    static invalidateCache() {
        // Clear expired cache entries
    }
}
```

**`performance-monitor.js`** - Performance tracking
```javascript
class PerformanceMonitor {
    static startTimer(name) {
        // Start performance timer
    }
    
    static endTimer(name) {
        // End timer and log results
    }
    
    static trackMetric(name, value) {
        // Track custom metrics
    }
}
```

#### CSS Architecture

**Component-based Structure**
```css
/* Base styles */
:root {
    --primary-color: #1291da;
    --secondary-color: #65acee;
    --spacing-unit: 8px;
}

/* Component styles */
.product-card {
    /* Product card styles */
}

.search-bar {
    /* Search interface styles */
}

.shopping-cart {
    /* Cart component styles */
}
```

## Data Flow

### Product Management Flow

```
Desktop App → JSON File → Git Commit → Git Push → Web App Sync
     ↓              ↓           ↓           ↓            ↓
  UI Update → File Write → Version → Remote → Cache Update
```

### Shopping Cart Flow

```
User Action → Cart Update → localStorage → UI Refresh → Persistence
     ↓             ↓            ↓            ↓            ↓
Add to Cart → Modify Array → Store Data → Re-render → Cross-tab Sync
```

### Search and Filter Flow

```
User Input → Debounce → Filter Logic → Results → UI Update
     ↓          ↓           ↓           ↓         ↓
  Keystroke → Wait 300ms → Apply → Cache → Render
```

## API Reference

### Desktop Application API

#### ProductManager Class

**`add_product(product_data: dict) -> bool`**
- Adds new product to catalog
- Validates required fields
- Returns success status

**`update_product(product_id: str, updates: dict) -> bool`**
- Updates existing product
- Merges updates with existing data
- Returns success status

**`delete_product(product_id: str) -> bool`**
- Removes product from catalog
- Handles cascade deletions
- Returns success status

**`get_product(product_id: str) -> dict`**
- Retrieves single product
- Returns product data or None

**`get_all_products() -> list`**
- Returns all products
- Includes filtering options

#### DataSynchronizer Class

**`sync_to_web() -> bool`**
- Synchronizes data to web store
- Commits and pushes changes
- Returns sync status

**`backup_data() -> str`**
- Creates data backup
- Returns backup file path

### Web Application API

#### StoreApp Class

**`loadProducts() -> Promise<Array>`**
- Loads products from JSON
- Implements caching
- Returns product array

**`searchProducts(query: string, filters: object) -> Array`**
- Searches and filters products
- Returns matching products

**`addToCart(productId: string, quantity: number) -> boolean`**
- Adds product to shopping cart
- Updates cart state
- Returns success status

#### CacheManager Class

**`CacheManager.cacheProducts(products: Array) -> void`**
- Caches product data
- Sets expiration time

**`CacheManager.getCachedProducts() -> Array|null`**
- Retrieves cached products
- Returns null if expired

## Database Schema

### Product Data Structure

```json
{
  "id": "string (unique identifier)",
  "title": "string (product name)",
  "description": "string (product description)",
  "price": "number (price in cents)",
  "category": "string (product category)",
  "discipline": "string (sports discipline)",
  "gender": "string (target gender)",
  "images": ["array of image paths"],
  "stock": "number (available quantity)",
  "variants": [
    {
      "id": "string",
      "size": "string",
      "color": "string",
      "stock": "number",
      "price_modifier": "number"
    }
  ],
  "metadata": {
    "created_at": "ISO date string",
    "updated_at": "ISO date string",
    "created_by": "string (user identifier)"
  }
}
```

### Cart Data Structure

```json
{
  "items": [
    {
      "product_id": "string",
      "variant_id": "string (optional)",
      "quantity": "number",
      "added_at": "ISO date string"
    }
  ],
  "metadata": {
    "created_at": "ISO date string",
    "updated_at": "ISO date string",
    "session_id": "string"
  }
}
```

### History Data Structure

```json
{
  "id": "string (unique identifier)",
  "action": "string (ADD|UPDATE|DELETE)",
  "entity_type": "string (PRODUCT|INVENTORY)",
  "entity_id": "string",
  "changes": "object (before/after data)",
  "user": "string (user identifier)",
  "timestamp": "ISO date string",
  "metadata": "object (additional context)"
}
```

## Performance Optimization

### Caching Strategy

#### Browser Caching
```javascript
// Cache products with 1-hour TTL
const CACHE_TTL = 60 * 60 * 1000; // 1 hour

class CacheManager {
    static cacheProducts(products) {
        const cacheData = {
            data: products,
            timestamp: Date.now(),
            ttl: CACHE_TTL
        };
        localStorage.setItem('products_cache', JSON.stringify(cacheData));
    }
}
```

#### Image Optimization
```css
/* Lazy loading images */
img {
    loading: lazy;
    decoding: async;
}

/* Responsive images */
img {
    width: 100%;
    height: auto;
    object-fit: cover;
}
```

### Code Splitting

#### Dynamic Imports
```javascript
// Load modules on demand
async function loadSearchModule() {
    const { SearchEngine } = await import('./search-engine.js');
    return new SearchEngine();
}

// Load on user interaction
document.addEventListener('focus', async (e) => {
    if (e.target.matches('.search-input')) {
        const searchEngine = await loadSearchModule();
        searchEngine.init();
    }
});
```

### Performance Monitoring

#### Core Web Vitals
```javascript
// Monitor Largest Contentful Paint
new PerformanceObserver((list) => {
    const entries = list.getEntries();
    const lastEntry = entries[entries.length - 1];
    console.log('LCP:', lastEntry.startTime);
}).observe({ entryTypes: ['largest-contentful-paint'] });

// Monitor Cumulative Layout Shift
let clsValue = 0;
new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
        if (!entry.hadRecentInput) {
            clsValue += entry.value;
        }
    }
}).observe({ entryTypes: ['layout-shift'] });
```

## Security Implementation

### Input Validation

#### Desktop Application
```python
def validate_product_data(data):
    """Validate product data before saving"""
    required_fields = ['title', 'price', 'category']
    
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValueError(f"Missing required field: {field}")
    
    # Sanitize string inputs
    data['title'] = sanitize_string(data['title'])
    data['description'] = sanitize_string(data.get('description', ''))
    
    # Validate numeric inputs
    if not isinstance(data['price'], (int, float)) or data['price'] < 0:
        raise ValueError("Price must be a positive number")
    
    return data
```

#### Web Application
```javascript
function sanitizeInput(input) {
    // Remove script tags and dangerous content
    return input
        .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
        .replace(/javascript:/gi, '')
        .replace(/on\w+\s*=/gi, '');
}

function validateProductData(data) {
    const errors = [];
    
    if (!data.title || data.title.trim().length === 0) {
        errors.push('Title is required');
    }
    
    if (!data.price || data.price <= 0) {
        errors.push('Price must be greater than 0');
    }
    
    return { isValid: errors.length === 0, errors };
}
```

### Data Protection

#### Local Storage Security
```javascript
// Encrypt sensitive data before storing
function encryptData(data, key) {
    // Simple encryption (use proper crypto in production)
    return btoa(JSON.stringify(data));
}

function decryptData(encryptedData, key) {
    try {
        return JSON.parse(atob(encryptedData));
    } catch (error) {
        console.error('Decryption failed:', error);
        return null;
    }
}
```

## Testing Framework

### Unit Testing

#### Desktop Application Tests
```python
import unittest
from product_manager import ProductManager

class TestProductManager(unittest.TestCase):
    def setUp(self):
        self.manager = ProductManager()
    
    def test_add_product(self):
        product_data = {
            'title': 'Test Product',
            'price': 100,
            'category': 'Test'
        }
        result = self.manager.add_product(product_data)
        self.assertTrue(result)
    
    def test_invalid_product(self):
        with self.assertRaises(ValueError):
            self.manager.add_product({})
```

#### Web Application Tests
```javascript
// Unit tests using built-in test framework
class TestSuite {
    static testCacheManager() {
        const products = [{ id: '1', title: 'Test' }];
        CacheManager.cacheProducts(products);
        
        const cached = CacheManager.getCachedProducts();
        console.assert(cached.length === 1, 'Cache should store products');
        console.assert(cached[0].id === '1', 'Cache should preserve data');
    }
    
    static testSearchEngine() {
        const engine = new SearchEngine();
        const products = [
            { id: '1', title: 'Red Shirt', category: 'Clothing' },
            { id: '2', title: 'Blue Pants', category: 'Clothing' }
        ];
        
        engine.indexProducts(products);
        const results = engine.search('red');
        console.assert(results.length === 1, 'Search should find matching products');
    }
}
```

### Integration Testing

#### End-to-End Tests
```javascript
class E2ETests {
    static async testProductWorkflow() {
        // Test complete product browsing workflow
        await this.loadProducts();
        await this.searchProducts('test');
        await this.addToCart('product-1');
        await this.verifyCartContents();
    }
    
    static async testDataSync() {
        // Test desktop-web synchronization
        await this.simulateDesktopUpdate();
        await this.verifyWebUpdate();
    }
}
```

## Deployment Guide

### Development Environment

#### Prerequisites
```bash
# Python dependencies
pip install customtkinter pillow gitpython

# Node.js (for development tools)
npm install -g http-server

# Git configuration
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

#### Local Development
```bash
# Start desktop application
python customtk.py

# Serve web application
cd html
python -m http.server 8000
# or
npx http-server -p 8000
```

### Production Deployment

#### Web Store Deployment
```bash
# Build optimization
npm run build

# Deploy to static hosting
# - Copy html/ directory to web server
# - Configure proper MIME types
# - Enable gzip compression
# - Set cache headers
```

#### Desktop Application Distribution
```bash
# Create executable (using PyInstaller)
pip install pyinstaller
pyinstaller --onefile --windowed customtk.py

# Create installer (using NSIS or similar)
# Package with dependencies and data files
```

### Environment Configuration

#### Production Settings
```python
# config.py
PRODUCTION = True
DEBUG = False
GIT_REMOTE_URL = "https://github.com/your-repo/deportes-guemes.git"
BACKUP_INTERVAL = 3600  # 1 hour
CACHE_TTL = 1800  # 30 minutes
```

#### Web Configuration
```javascript
// config.js
const CONFIG = {
    PRODUCTION: true,
    API_BASE_URL: 'https://api.deportesguemes.com',
    CACHE_TTL: 30 * 60 * 1000, // 30 minutes
    PERFORMANCE_MONITORING: true
};
```

## Maintenance Procedures

### Regular Maintenance Tasks

#### Daily Tasks
- Monitor error logs
- Check system performance
- Verify data synchronization
- Review backup status

#### Weekly Tasks
- Clean up old cache files
- Update product images
- Review performance metrics
- Test backup restoration

#### Monthly Tasks
- Update dependencies
- Security audit
- Performance optimization review
- User feedback analysis

### Backup Procedures

#### Automated Backups
```python
import schedule
import time

def backup_data():
    """Create automated backup"""
    backup_manager = BackupManager()
    backup_file = backup_manager.create_backup()
    print(f"Backup created: {backup_file}")

# Schedule daily backups
schedule.every().day.at("02:00").do(backup_data)

while True:
    schedule.run_pending()
    time.sleep(60)
```

#### Manual Backup
```bash
# Create manual backup
python backup_system.py --create-backup

# Restore from backup
python backup_system.py --restore backup_20231201_120000.json
```

### Update Procedures

#### System Updates
1. **Backup current data**
2. **Test updates in development**
3. **Deploy to production**
4. **Verify functionality**
5. **Monitor for issues**

#### Dependency Updates
```bash
# Check for updates
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update all packages
pip freeze > requirements.txt
pip install -r requirements.txt --upgrade
```

## Troubleshooting Guide

### Common Issues

#### Desktop Application Issues

**Application Won't Start**
```python
# Check Python version
import sys
print(sys.version)

# Check dependencies
try:
    import customtkinter
    import PIL
    import git
    print("All dependencies available")
except ImportError as e:
    print(f"Missing dependency: {e}")
```

**Git Synchronization Fails**
```python
# Check Git configuration
import git
repo = git.Repo('.')
print(f"Remote URL: {repo.remotes.origin.url}")
print(f"Current branch: {repo.active_branch}")

# Test connectivity
try:
    repo.remotes.origin.fetch()
    print("Git connectivity OK")
except Exception as e:
    print(f"Git error: {e}")
```

#### Web Application Issues

**Performance Problems**
```javascript
// Check performance metrics
console.log('Performance timing:', performance.timing);

// Check memory usage
if (performance.memory) {
    console.log('Memory usage:', {
        used: performance.memory.usedJSHeapSize,
        total: performance.memory.totalJSHeapSize,
        limit: performance.memory.jsHeapSizeLimit
    });
}

// Check cache status
const cacheSize = Object.keys(localStorage).length;
console.log(`LocalStorage items: ${cacheSize}`);
```

**Search Not Working**
```javascript
// Debug search functionality
function debugSearch(query) {
    console.log('Search query:', query);
    console.log('Products loaded:', window.products?.length || 0);
    console.log('Active filters:', window.activeFilters);
    
    const results = searchProducts(query);
    console.log('Search results:', results.length);
    return results;
}
```

### Error Logging

#### Desktop Application Logging
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Log errors
try:
    # Application code
    pass
except Exception as e:
    logger.error(f"Error in function: {e}", exc_info=True)
```

#### Web Application Logging
```javascript
// Error tracking
class ErrorTracker {
    static logError(error, context = {}) {
        const errorData = {
            message: error.message,
            stack: error.stack,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userAgent: navigator.userAgent,
            context
        };
        
        // Store locally
        const errors = JSON.parse(localStorage.getItem('error_log') || '[]');
        errors.push(errorData);
        localStorage.setItem('error_log', JSON.stringify(errors.slice(-100)));
        
        // Send to monitoring service (if available)
        if (window.errorReporting) {
            window.errorReporting.send(errorData);
        }
    }
}

// Global error handler
window.addEventListener('error', (event) => {
    ErrorTracker.logError(event.error, {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno
    });
});
```

### Performance Monitoring

#### System Metrics
```javascript
// Monitor key metrics
setInterval(() => {
    const metrics = {
        timestamp: Date.now(),
        memory: performance.memory ? {
            used: performance.memory.usedJSHeapSize,
            total: performance.memory.totalJSHeapSize
        } : null,
        timing: {
            loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
            domReady: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart
        },
        resources: performance.getEntriesByType('resource').length
    };
    
    // Store metrics
    const allMetrics = JSON.parse(localStorage.getItem('performance_metrics') || '[]');
    allMetrics.push(metrics);
    localStorage.setItem('performance_metrics', JSON.stringify(allMetrics.slice(-100)));
}, 60000); // Every minute
```

---

## Support and Maintenance

### Contact Information
- **Technical Lead**: [Name] - [email]
- **System Administrator**: [Name] - [email]
- **Repository**: [Git repository URL]
- **Documentation**: [Documentation URL]

### Version History
- **v1.0.0**: Initial release with core functionality
- **v1.1.0**: Performance optimizations and accessibility improvements
- **v1.2.0**: Enhanced testing framework and monitoring

---

*Last updated: [Current Date]*
*Document version: 1.0.0*