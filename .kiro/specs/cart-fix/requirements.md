# Requirements Document

## Introduction

The shopping cart functionality in the Deportes Güemes web application is currently not working properly. Users are unable to see products they've added to their cart, and the cart always shows as empty even when products have been added. This critical e-commerce functionality needs to be fixed to ensure customers can properly manage their shopping experience.

## Requirements

### Requirement 1

**User Story:** As a customer, I want to see products I've added to my cart when I visit the cart page, so that I can review my selections before making a purchase inquiry.

#### Acceptance Criteria

1. WHEN a user adds products to their cart from the main store page THEN the products SHALL be visible in the cart page
2. WHEN a user visits the cart page THEN the cart SHALL display all previously added products with correct details (name, price, quantity, image)
3. WHEN the cart has products THEN the cart counter SHALL show the correct number of items
4. WHEN the cart is empty THEN the system SHALL display an appropriate empty cart message

### Requirement 2

**User Story:** As a customer, I want my cart contents to persist across browser sessions, so that I don't lose my selections when I close and reopen the browser.

#### Acceptance Criteria

1. WHEN a user adds products to their cart THEN the cart data SHALL be saved to browser storage
2. WHEN a user closes and reopens their browser THEN their cart contents SHALL be restored
3. WHEN cart data is corrupted or invalid THEN the system SHALL handle the error gracefully and show an empty cart
4. WHEN cart data is saved THEN it SHALL include all necessary product information (id, title, price, quantity, image, variants)

### Requirement 3

**User Story:** As a customer, I want to modify quantities and remove items from my cart, so that I can adjust my order before inquiring about purchase.

#### Acceptance Criteria

1. WHEN a user clicks the increase quantity button THEN the product quantity SHALL increment by 1
2. WHEN a user clicks the decrease quantity button THEN the product quantity SHALL decrement by 1
3. WHEN a product quantity reaches 0 THEN the product SHALL be removed from the cart
4. WHEN a user clicks the remove button THEN the product SHALL be immediately removed from the cart
5. WHEN cart quantities change THEN the total price SHALL update automatically

### Requirement 4

**User Story:** As a customer, I want to see accurate pricing and totals in my cart, so that I know the cost of my potential purchase.

#### Acceptance Criteria

1. WHEN products are displayed in the cart THEN each product SHALL show its individual price
2. WHEN products have quantities greater than 1 THEN the system SHALL show both unit price and total price per product
3. WHEN the cart has multiple products THEN the system SHALL calculate and display the correct subtotal
4. WHEN cart contents change THEN all pricing information SHALL update immediately

### Requirement 5

**User Story:** As a customer, I want to send my cart contents via WhatsApp for purchase inquiry, so that I can complete my purchase through the store's preferred communication channel.

#### Acceptance Criteria

1. WHEN a user clicks the WhatsApp consultation button THEN a WhatsApp message SHALL be generated with all cart products
2. WHEN the WhatsApp message is generated THEN it SHALL include product names, quantities, prices, and any selected variants
3. WHEN the WhatsApp link is created THEN it SHALL open in a new tab/window
4. WHEN the cart is empty THEN the WhatsApp button SHALL be disabled or show an appropriate message