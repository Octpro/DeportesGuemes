# Design Document

## Overview

The cart size selection functionality needs to be redesigned to provide proper visual feedback, state management, and persistence. The current implementation has issues with:

1. Visual state not updating when sizes are selected
2. Selected sizes not being properly stored and retrieved
3. Lack of clear feedback to users about their selections
4. Inconsistent behavior between cart operations

## Architecture

### Current State Analysis

The current cart system uses:
- `CartDataManager` class for cart operations and localStorage persistence
- Event delegation for checkbox handling in `carrito.js`
- Dynamic HTML generation for size selection checkboxes
- `actualizarTallesSeleccionados()` function to update product data
- `actualizarResumenTalles()` function to update visual display

### Proposed Solution Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Cart Size Selection System               │
├─────────────────────────────────────────────────────────────┤
│  UI Layer                                                   │
│  ├── Size Selection Checkboxes (Visual State)              │
│  ├── Size Summary Display (Selected Sizes)                 │
│  └── Visual Feedback (Animations, Highlights)              │
├─────────────────────────────────────────────────────────────┤
│  State Management Layer                                     │
│  ├── SizeSelectionManager (New Component)                  │
│  ├── Visual State Synchronizer                             │
│  └── Event Handler Coordinator                             │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                 │
│  ├── CartDataManager (Enhanced)                            │
│  ├── Product Size Data Structure                           │
│  └── localStorage Persistence                              │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. SizeSelectionManager (New Component)

```javascript
class SizeSelectionManager {
    constructor(cartManager) {
        this.cartManager = cartManager;
        this.eventHandlers = new Map();
    }
    
    // Core methods
    initializeProductSizes(productId, availableSizes, selectedSizes)
    updateSizeSelection(productId, size, isSelected)
    getSelectedSizes(productId)
    validateSizeSelection(productId, sizes)
    syncVisualState(productId)
}
```

### 2. Enhanced CartDataManager

Add methods to handle size selection:

```javascript
// New methods to add to CartDataManager
updateProductSizes(productId, selectedSizes)
getProductSizes(productId)
validateProductSizes(product)
```

### 3. Visual State Components

#### Size Checkbox Component
```html
<label class="talle-checkbox" data-size="{size}" data-product-id="{productId}">
    <input type="checkbox" value="{size}" class="talle-input">
    <span class="talle-label">{size}</span>
    <span class="talle-check-indicator">
        <i class="bi bi-check-circle-fill"></i>
    </span>
</label>
```

#### Size Summary Component
```html
<div class="talles-summary" data-product-id="{productId}">
    <span class="talles-label">Talles disponibles: {availableSizes}</span>
    <span class="talles-selected" data-empty-text="Ningún talle seleccionado">
        Seleccionados: {selectedSizes}
    </span>
</div>
```

## Data Models

### Enhanced Product Structure

```javascript
{
    id: "string",
    titulo: "string",
    precio: number,
    cantidad: number,
    talles: ["S", "M", "L", "XL"], // Available sizes
    tallesSeleccionados: ["M", "L"], // Selected sizes (enhanced)
    sizeSelectionState: {
        lastUpdated: timestamp,
        isValid: boolean,
        hasSelection: boolean
    }
}
```

### Size Selection Event Structure

```javascript
{
    type: "size_selection_change",
    productId: "string",
    size: "string",
    isSelected: boolean,
    allSelectedSizes: ["M", "L"],
    timestamp: number
}
```

## Error Handling

### Size Selection Validation

1. **Invalid Size Selection**: Prevent selection of unavailable sizes
2. **Data Corruption Recovery**: Restore valid state if data is corrupted
3. **Storage Failures**: Graceful fallback to in-memory state
4. **UI Sync Failures**: Re-sync visual state with data

### Error Recovery Strategies

```javascript
// Error handling patterns
try {
    updateSizeSelection(productId, size, isSelected);
} catch (error) {
    console.error('Size selection failed:', error);
    // Fallback: restore previous state
    restorePreviousState(productId);
    // Show user feedback
    showErrorFeedback('Error updating size selection');
}
```

## Testing Strategy

### Unit Tests

1. **SizeSelectionManager Tests**
   - Size selection/deselection
   - State persistence
   - Data validation
   - Error handling

2. **CartDataManager Enhancement Tests**
   - Size data storage/retrieval
   - Product validation with sizes
   - localStorage persistence

3. **Visual State Tests**
   - Checkbox state synchronization
   - Summary display updates
   - Animation triggers

### Integration Tests

1. **Cart Operations with Sizes**
   - Add product with size selection
   - Update quantities with sizes
   - Remove products with sizes
   - Clear cart with size data

2. **Cross-Page Persistence**
   - Navigate away and return
   - Browser refresh
   - localStorage corruption recovery

3. **WhatsApp Message Generation**
   - Include selected sizes in message
   - Handle products without size selection
   - Format message correctly

### User Experience Tests

1. **Visual Feedback**
   - Immediate checkbox response
   - Summary updates
   - Error state display

2. **Accessibility**
   - Screen reader compatibility
   - Keyboard navigation
   - Focus management

3. **Mobile Responsiveness**
   - Touch targets
   - Checkbox sizing
   - Summary display

## Implementation Phases

### Phase 1: Core Size Selection Logic
- Create SizeSelectionManager class
- Enhance CartDataManager with size methods
- Implement basic size selection/deselection

### Phase 2: Visual State Management
- Implement visual state synchronization
- Add CSS animations and transitions
- Create responsive size selection UI

### Phase 3: Persistence and Recovery
- Enhance localStorage handling for sizes
- Implement error recovery mechanisms
- Add data validation and cleanup

### Phase 4: Integration and Polish
- Integrate with existing cart operations
- Update WhatsApp message generation
- Add comprehensive error handling

## CSS Enhancements

### Size Selection Styling

```css
.talle-checkbox {
    position: relative;
    display: inline-flex;
    align-items: center;
    padding: 8px 12px;
    border: 2px solid var(--clr-border);
    border-radius: var(--border-radius-sm);
    cursor: pointer;
    transition: all 0.2s ease;
    user-select: none;
}

.talle-checkbox.selected {
    border-color: var(--clr-main);
    background-color: var(--clr-main-light);
    color: var(--clr-main);
}

.talle-checkbox:hover {
    border-color: var(--clr-main);
    transform: translateY(-1px);
}

.talle-input {
    position: absolute;
    opacity: 0;
    pointer-events: none;
}

.talle-check-indicator {
    opacity: 0;
    transition: opacity 0.2s ease;
    margin-left: 4px;
}

.talle-checkbox.selected .talle-check-indicator {
    opacity: 1;
}
```

### Animation System

```css
@keyframes sizeSelectionPulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

.talle-checkbox.just-selected {
    animation: sizeSelectionPulse 0.3s ease;
}

.talles-summary {
    transition: all 0.3s ease;
}

.talles-selected.updating {
    opacity: 0.7;
    transform: translateX(2px);
}
```

## Performance Considerations

### Optimization Strategies

1. **Event Delegation**: Use single event listener for all size checkboxes
2. **Debounced Updates**: Prevent excessive localStorage writes
3. **Lazy State Sync**: Only sync visual state when necessary
4. **Memory Management**: Clean up event listeners and references

### Monitoring

- Track size selection performance
- Monitor localStorage usage
- Log error rates and recovery success
- Measure user interaction response times