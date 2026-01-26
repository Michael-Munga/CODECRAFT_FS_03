# Layer 1: Data Integrity & Persistence - Teaching Guide

This document explains the fundamental concepts of data integrity and persistence using your ecommerce project as practical examples.

## Current Architecture Analysis

### Database Schema Structure

In your ecommerce project, the current database schema includes:

- **Users Table**: Stores user information with authentication data
- **Categories Table**: Product categories
- **Products Table**: Product details with pricing and inventory
- **Carts Table**: User shopping carts
- **CartItems Table**: Individual items in carts
- **Orders Table**: Purchase orders
- **OrderItems Table**: Items within orders

### Issues Identified in Current Implementation

1. **Missing Foreign Key Constraints**: Some relationships lack proper foreign key constraints
2. **Transaction Handling**: Payment processing lacks atomicity for stock updates
3. **Query Performance**: Potential N+1 query issues in some endpoints
4. **Data Validation**: Missing server-side validation for business rules

## Core Concepts of Data Integrity & Persistence

### 1. Foreign Keys & Constraints

Foreign keys ensure referential integrity between tables. In your models.py:

```python
# GOOD: Proper foreign key relationships
class Product(db.Model, SerializerMixin):
    __tablename__ = 'products'

    # Foreign key to Category
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))  # <-- FOREIGN KEY
    category = relationship("Category", back_populates="products")

class CartItem(db.Model, SerializerMixin):
    __tablename__ = 'cart_items'

    # Foreign keys to Cart and Product
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)      # <-- FOREIGN KEY
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False) # <-- FOREIGN KEY
    product = relationship("Product", back_populates="cart_items")
    cart = relationship("Cart", back_populates="items")
```

**Why this matters**: Without foreign keys, you could have orphaned records. For example, a CartItem could reference a product that no longer exists, causing errors in your application.

### 2. Transactions for Multi-Step Operations

Transactions ensure that related operations either ALL succeed or ALL fail. In your payment process, here's how it should work:

```python
# PROPER TRANSACTION HANDLING
def process_payment_with_stock_reservation():
    try:
        # Start transaction
        db.session.begin_nested()  # or db.session.begin() for full transaction

        # Step 1: Check and reserve stock
        for cart_item in cart.items:
            product = Product.query.get(cart_item.product_id)
            if product.stock < cart_item.quantity:
                raise Exception(f"Not enough stock for {product.name}")
            product.stock -= cart_item.quantity  # Reserve stock

        # Step 2: Create order
        order = Order(user_id=user_id, total_amount=total_amount, status="pending")
        db.session.add(order)
        db.session.flush()  # Get order ID without committing

        # Step 3: Create order items
        for cart_item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            db.session.add(order_item)

        # Step 4: Clear cart
        for cart_item in cart.items:
            db.session.delete(cart_item)

        # Commit all changes atomically
        db.session.commit()
        return order.id

    except Exception as e:
        # Rollback all changes if anything fails
        db.session.rollback()
        raise e  # Re-raise the exception
```

**Why this matters**: Without transactions, if money gets deducted but the order isn't created, or if stock is reduced but the payment fails, you'll have data inconsistency.

### 3. Query Optimization & N+1 Problems

N+1 queries occur when you fetch a list of records and then loop through them making individual queries for related data:

```python
# BAD: N+1 Query Problem
def get_products_with_categories_bad():
    products = Product.query.all()  # Fetches all products (1 query)
    result = []
    for product in products:
        # Each iteration triggers another query to get the category (N queries)
        result.append({
            'name': product.name,
            'category': product.category.name  # <-- N+1 problem!
        })
    return result

# GOOD: Optimized with eager loading
def get_products_with_categories_good():
    # Use joinedload to fetch related data in a single query
    from sqlalchemy.orm import joinedload

    products = Product.query.options(joinedload(Product.category)).all()
    result = []
    for product in products:
        # No additional query needed - category already loaded
        result.append({
            'name': product.name,
            'category': product.category.name  # <-- No extra query
        })
    return result
```

**Why this matters**: As your database grows, N+1 queries will severely impact performance. A page that takes 10ms with proper queries could take 1000ms+ with N+1 queries.

### 4. Indexes for Performance

Indexes speed up data retrieval. In your current schema, you should consider adding indexes:

```python
# Example of adding indexes to your models
class Order(db.Model, SerializerMixin):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)  # <-- INDEX
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="pending", index=True)  # <-- INDEX for filtering
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)  # <-- INDEX for sorting

    # Composite index for common query patterns
    __table_args__ = (
        db.Index('idx_user_status_created', 'user_id', 'status', 'created_at'),  # <-- COMPOSITE INDEX
    )
```

**Why this matters**: Without proper indexing, queries that filter, sort, or join on frequently accessed columns become slow as data grows.

### 5. Migration Strategy

Your project uses Alembic for migrations. Here's a proper migration strategy:

```python
# Example of a safe migration for adding a new column with constraints
"""Add stock_alert_threshold to products table

Revision ID: abc123def456
Revises: 007cab3603c2
Create Date: 2026-01-12 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'abc123def456'
down_revision = '007cab3603c2'  # Previous migration ID
branch_labels = None
depends_on = None


def upgrade():
    # Add the new column as nullable first
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('stock_alert_threshold', sa.Integer(), nullable=True))

    # Update existing records with default values if needed
    connection = op.get_bind()
    connection.execute(
        "UPDATE products SET stock_alert_threshold = 5 WHERE stock_alert_threshold IS NULL"
    )

    # Now make it non-nullable
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.alter_column('stock_alert_threshold', nullable=False)


def downgrade():
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_column('stock_alert_threshold')
```

**Why this matters**: Production databases can't afford downtime. Safe migrations ensure zero-downtime deployments.

## Real-World Issues in Your Current Code

### Issue 1: Race Condition in Stock Updates

```python
# CURRENT PROBLEMATIC CODE in payment process:
def process_payment():
    # Multiple users could check stock at the same time
    for cart_item in cart.items:
        product = Product.query.get(cart_item.product_id)  # Read stock
        if product.stock >= cart_item.quantity:  # Check happens here
            product.stock -= cart_item.quantity  # But update happens later
            # Another user could have purchased the same item in between!
```

### Issue 2: No Business Logic Validation

```python
# MISSING: Validation for minimum stock, max quantities, etc.
def add_to_cart(product_id, quantity):
    product = Product.query.get(product_id)
    # Should validate: quantity > 0, quantity <= available stock, max per user, etc.
```

### Issue 3: Missing Unique Constraints

```python
# Your User model has unique constraints on email and phone_number (GOOD!)
email = db.Column(db.String(100), unique=True, nullable=False)  # <-- GOOD
phone_number = db.Column(db.String(20), unique=True, nullable=False)  # <-- GOOD

# But missing constraints for business logic
# Example: Prevent duplicate cart items more elegantly
```

## Solutions & Best Practices

### 1. Implementing Proper Transaction Isolation

```python
from sqlalchemy import text

def purchase_with_stock_reservation(user_id, cart_id):
    try:
        # Use SERIALIZABLE isolation level to prevent race conditions
        db.session.connection(execution_options={'isolation_level': 'SERIALIZABLE'})

        # Lock the products rows for update to prevent concurrent modifications
        cart_items = db.session.query(CartItem)\
            .join(Product)\
            .filter(CartItem.cart_id == cart_id)\
            .with_for_update()  # <-- LOCK ROWS FOR UPDATE

        # Validate stock availability
        for cart_item in cart_items:
            if cart_item.product.stock < cart_item.quantity:
                raise ValueError(f"Insufficient stock for {cart_item.product.name}")

        # Deduct stock
        for cart_item in cart_items:
            cart_item.product.stock -= cart_item.quantity

        # Process order creation...
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise e
```

### 2. Adding Custom Validators

```python
from sqlalchemy.orm import validates

class Product(db.Model, SerializerMixin):

    @validates('stock')
    def validate_stock(self, key, value):
        if value < 0:
            raise ValueError("Stock cannot be negative")
        # Add business logic validation
        if value > 10000:  # Maximum inventory limit
            raise ValueError("Stock exceeds maximum allowed inventory")
        return value

    @validates('price')
    def validate_price(self, key, value):
        if value <= 0:
            raise ValueError("Price must be positive")
        if value > 100000:  # Price cap
            raise ValueError("Price exceeds maximum allowed value")
        return value
```

### 3. Query Optimization Techniques

```python
# Efficient product listing with filters
def get_products_with_filters(category_id=None, min_price=None, max_price=None, page=1, per_page=20):
    query = Product.query.options(joinedload(Product.category))

    if category_id:
        query = query.filter(Product.category_id == category_id)
    if min_price:
        query = query.filter(Product.price >= min_price)
    if max_price:
        query = query.filter(Product.price <= max_price)

    # Paginate to avoid loading too much data
    return query.paginate(page=page, per_page=per_page, error_out=False)

# Bulk operations for better performance
def bulk_update_stock(changes):
    # Update multiple products in a single query instead of individual updates
    stmt = (
        db.update(Product)
        .where(Product.id.in_(changes.keys()))
        .values({Product.stock: db.case(changes, value=Product.id)})
    )
    db.session.execute(stmt)
    db.session.commit()
```

## Connection to Frontend

The backend data integrity directly affects frontend behavior:

### 1. Real-time Stock Updates

```javascript
// Frontend can subscribe to stock updates via WebSocket
// When backend processes orders, it broadcasts stock changes
socket.on("stock_updated", (data) => {
  // Update UI to reflect new stock levels
  updateProductStock(data.productId, data.newStock);
});

// Or poll backend API endpoints for stock status
async function checkStock(productId) {
  const response = await fetch(`/api/products/${productId}/stock`);
  const { stock, reserved } = await response.json();
  // Update UI accordingly
}
```

### 2. Consistent Error Handling

```javascript
// Backend sends structured errors that frontend can handle appropriately
try {
  const response = await fetch("/api/payment/process", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      /* payment data */
    }),
  });

  if (!response.ok) {
    const error = await response.json();

    // Handle specific business logic errors
    if (error.code === "INSUFFICIENT_STOCK") {
      showNotification("Some items are out of stock");
      refreshCart();
    } else if (error.code === "PAYMENT_FAILED") {
      showNotification("Payment failed, please try again");
    }
  }
} catch (err) {
  console.error("Payment error:", err);
}
```

## Summary

Data integrity & persistence is foundational to any reliable application. The concepts covered here ensure that:

1. **Data doesn't get corrupted** - Through proper constraints and validation
2. **Transactions are atomic** - Through proper transaction handling
3. **Performance scales** - Through indexing and query optimization
4. **Changes are safe** - Through proper migration strategies
5. **Business logic is enforced** - Through custom validators and constraints

These principles are essential for building systems that users can trust with their money and data.
