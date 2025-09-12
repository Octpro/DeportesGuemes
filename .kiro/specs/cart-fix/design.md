# Design Document

## Overview

The cart functionality fix involves addressing JavaScript dependency issues, implementing robust cart persistence, and ensuring proper data flow between the main store page and cart page. The solution will maintain the existing UI design while fixing the underlying data management and persistence mechanisms.

## Architecture

### Current Architecture Issues
- Missing or broken JavaScript dependencies causing initialization failures
- Inconsistent cart data persistence between localStorage and custom persistence manager
- Race conditions in cart initialization timing
- Incomplete error handling for cart data corruption

### Proposed Architecture
- Simplified, reliable cart persistence using localStorage as primary storage
- Defensive programming with fallback mechanisms
- Proper initialization order and dependency management
- Centralized cart state management

## Components and Interfaces

### 1. Cart Data Manager
**Purpose:** Centralized cart data operations with robust error handling

**Interface:**
```javascript
class CartDataManager {
    loadCart()           // Returns array of cart products
    saveCart(products)   // Saves cart products to storage
    addProduct(product)  // Adds or updates product in cart
    removeProduct(id)    // Removes product from cart
    updateQuantity(id, quantity) // Updates product quantity
    clearCart()          // Empties the cart
    getCartSummary()     // Returns cart totals and counts
}
```

### 2. Cart UI Controller
**Purpose:** Manages cart page display and user interactions

**Interface:**
```javascript
class CartUIController {
    renderCart(products)     // Renders cart products in UI
    renderEmptyState()       // Shows empty cart message
    updateCartSummary(data)  // Updates totals and counters
    bindEventHandlers()      // Attaches click handlers
    showFeedback(message)    // Shows user feedback
}
```

### 3. Product Data Service
**Purpose:** Handles product data loading and validation

**Interface:**
```javascript
class ProductDataService {
    loadProducts()           // Loads products from JSON
    validateProduct(product) // Validates product data structure
    findProductById(id)      // Finds product by ID
}
```

## Data Models

### Cart Product Model
```javascript
{
    id: string,              // Unique product identifier
    titulo: string,          // Product title
    precio: number,          // Unit price
    cantidad: number,        // Quantity in cart
    imagen: string,          // Product image URL
    genero?: string,         // Gender category (optional)
    talles?: string[],       // Available sizes (optional)
    color?: string,          // Product color (optional)
    tallesSeleccionados?: string[], // Selected sizes (optional)
    addedAt: number          // Timestamp when added to cart
}
```

### Cart Summary Model
```javascript
{
    totalItems: number,      // Total quantity of all products
    subtotal: number,        // Sum of all product prices
    productCount: number     // Number of unique products
}
```

## Error Handling

### Storage Errors
- **Scenario:** localStorage is unavailable or quota exceeded
- **Handling:** Use in-memory storage with user notification
- **Fallback:** Session-based cart that clears on page refresh

### Data Corruption
- **Scenario:** Invalid JSON or missing required fields
- **Handling:** Clear corrupted data and start with empty cart
- **Logging:** Log errors for debugging without breaking user experience

### Product Loading Failures
- **Scenario:** productos.json fails to load
- **Handling:** Show error message and disable cart functionality
- **Retry:** Implement retry mechanism with exponential backoff

### Race Conditions
- **Scenario:** Cart operations before initialization complete
- **Handling:** Queue operations until initialization is complete
- **Timeout:** Set maximum wait time before showing error

## Testing Strategy

### Unit Tests
- Cart data operations (add, remove, update, clear)
- Data validation and sanitization
- Error handling for various failure scenarios
- Storage operations with mocked localStorage

### Integration Tests
- Full cart workflow from product addition to WhatsApp generation
- Cross-page cart persistence (main store → cart page)
- UI updates in response to data changes
- Error recovery scenarios

### Manual Testing Scenarios
1. Add products from main page, verify they appear in cart
2. Modify quantities and verify totals update correctly
3. Remove products and verify cart updates
4. Clear browser storage and verify empty cart handling
5. Test WhatsApp message generation with various product combinations
6. Test cart persistence across browser sessions

## Implementation Approach

### Phase 1: Core Cart Functionality
1. Implement simplified CartDataManager with localStorage
2. Fix cart initialization and loading in carrito.js
3. Ensure proper product display in cart page
4. Test basic add/remove/update operations

### Phase 2: UI Enhancements
1. Fix quantity controls and remove buttons
2. Implement proper cart summary calculations
3. Add loading states and error messages
4. Improve user feedback for cart operations

### Phase 3: Integration & Polish
1. Ensure cart counter updates across pages
2. Fix WhatsApp message generation
3. Add comprehensive error handling
4. Test cross-browser compatibility

## Security Considerations

### Data Validation
- Sanitize all product data before storage
- Validate product IDs against known products
- Prevent injection attacks in WhatsApp message generation

### Storage Security
- Don't store sensitive information in localStorage
- Implement data expiration for cart items
- Handle storage quota limits gracefully

## Performance Considerations

### Optimization Strategies
- Lazy load cart data only when needed
- Debounce quantity update operations
- Use efficient DOM manipulation for cart updates
- Minimize localStorage read/write operations

### Memory Management
- Clean up event listeners when not needed
- Avoid memory leaks in cart state management
- Implement proper cleanup on page unload