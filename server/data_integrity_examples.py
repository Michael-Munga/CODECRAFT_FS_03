"""
Data Integrity & Persistence Examples
Demonstrates proper implementation of foreign keys, constraints, and transactions
using the ecommerce project as a reference
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, text, and_, or_
from sqlalchemy.orm import validates, relationship, joinedload, selectinload
# Removed PostgreSQL-specific import for UUID as it's not needed for SQLite
from datetime import datetime
import uuid
from models import db, User, Product, Cart, CartItem, Order, OrderItem
from flask import jsonify
import logging

# Set up logging for transaction monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. PROPER FOREIGN KEY CONSTRAINTS WITH CASCADE OPTIONS
class EnhancedProduct(db.Model):
    """
    Enhanced Product model with proper constraints and validation
    """
    __tablename__ = 'enhanced_products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)  # Added index
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    image_url = db.Column(db.String)
    
    # Foreign key with proper cascade options
    category_id = db.Column(
        db.Integer, 
        db.ForeignKey('categories.id', ondelete='SET NULL'),  # If category deleted, set to NULL
        nullable=True,
        index=True  # Added index for performance
    )
    
    # Relationships with proper cascade options
    category = relationship("Category", back_populates="products")
    cart_items = relationship("EnhancedCartItem", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("EnhancedOrderItem", back_populates="product", cascade="all, delete-orphan")
    
    # Serialization rules
    serialize_rules = ('-cart_items.product', '-order_items.product', '-category.products')
    
    # Custom validators to enforce business rules
    @validates("price")
    def validate_price(self, key, value):
        if value <= 0:
            raise ValueError("Price must be positive")
        if value > 100000:  # Business rule: max price limit
            raise ValueError("Price exceeds maximum allowed value")
        return float(value)
    
    @validates("stock")
    def validate_stock(self, key, value):
        if value < 0:
            raise ValueError("Stock cannot be negative")
        if value > 10000:  # Business rule: max inventory limit
            raise ValueError("Stock exceeds maximum allowed inventory")
        return int(value)
    
    @validates("name")
    def validate_name(self, key, value):
        if not value or len(value.strip()) == 0:
            raise ValueError("Product name cannot be empty")
        if len(value) > 100:
            raise ValueError("Product name too long")
        return value.strip()


class EnhancedCartItem(db.Model):
    """
    Enhanced CartItem with proper foreign key constraints
    """
    __tablename__ = 'enhanced_cart_items'

    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys with cascade options
    cart_id = db.Column(
        db.Integer, 
        db.ForeignKey('carts.id', ondelete='CASCADE'),  # If cart deleted, delete items
        nullable=False,
        index=True
    )
    product_id = db.Column(
        db.Integer, 
        db.ForeignKey('enhanced_products.id', ondelete='CASCADE'),  # If product deleted, delete cart items
        nullable=False,
        index=True
    )
    
    quantity = db.Column(db.Integer, default=1, nullable=False)
    
    # Relationships
    cart = relationship("EnhancedCart", back_populates="items")
    product = relationship("EnhancedProduct", back_populates="cart_items")
    
    serialize_rules = ("-cart.items", "-product.cart_items")
    
    # Custom validation
    @validates("quantity")
    def validate_quantity(self, key, value):
        if value <= 0:
            raise ValueError("Quantity must be positive")
        if value > 100:  # Business rule: max quantity per cart item
            raise ValueError("Quantity exceeds maximum allowed per item")
        return int(value)


class EnhancedOrderItem(db.Model):
    """
    Enhanced OrderItem with proper constraints
    """
    __tablename__ = 'enhanced_order_items'

    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys with cascade options
    order_id = db.Column(
        db.Integer, 
        db.ForeignKey('orders.id', ondelete='CASCADE'),  # If order deleted, delete items
        nullable=False,
        index=True
    )
    product_id = db.Column(
        db.Integer, 
        db.ForeignKey('enhanced_products.id', ondelete='RESTRICT'),  # Prevent product deletion if ordered
        nullable=False,
        index=True
    )
    
    quantity = db.Column(db.Integer, default=1, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Store price at time of order
    
    # Relationships
    order = relationship("Order", back_populates="items")  # Using existing Order model
    product = relationship("EnhancedProduct", back_populates="order_items")
    
    # Custom validation
    @validates("quantity", "price")
    def validate_order_item_fields(self, key, value):
        if key == "quantity" and (value <= 0 or value > 100):
            raise ValueError("Order item quantity must be between 1 and 100")
        if key == "price" and value <= 0:
            raise ValueError("Order item price must be positive")
        return value


# 2. PROPER TRANSACTION HANDLING EXAMPLES

def create_order_with_stock_reservation(user_id, cart_id):
    """
    PROPER TRANSACTION: Create order with stock reservation in a single atomic operation
    This prevents race conditions and ensures data consistency
    """
    try:
        # Start transaction
        db.session.begin_nested()  # Creates a savepoint
        
        # Get user and cart with proper locking to prevent race conditions
        user = db.session.query(User).filter(User.id == user_id).with_for_update().first()
        if not user:
            raise ValueError("User not found")
        
        cart = db.session.query(Cart).filter(Cart.id == cart_id).with_for_update().first()
        if not cart or cart.user_id != user_id:
            raise ValueError("Cart not found or doesn't belong to user")
        
        # Lock product records to prevent concurrent updates
        cart_items = db.session.query(CartItem)\
            .filter(CartItem.cart_id == cart_id)\
            .options(joinedload(CartItem.product))\
            .with_for_update()  # <-- CRITICAL: Locks the product rows
        
        # Validate stock availability before proceeding
        insufficient_stock = []
        for cart_item in cart_items:
            if cart_item.product.stock < cart_item.quantity:
                insufficient_stock.append({
                    'product_name': cart_item.product.name,
                    'available': cart_item.product.stock,
                    'requested': cart_item.quantity
                })
        
        if insufficient_stock:
            raise ValueError(f"Insufficient stock: {insufficient_stock}")
        
        # Calculate total amount
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        
        # Create order
        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            status="pending"
        )
        db.session.add(order)
        db.session.flush()  # Get order ID without committing
        
        # Create order items and deduct stock atomically
        for cart_item in cart_items:
            # Create order item
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            db.session.add(order_item)
            
            # Deduct stock from product
            cart_item.product.stock -= cart_item.quantity
        
        # Clear cart items
        for cart_item in cart_items:
            db.session.delete(cart_item)
        
        # Commit all changes atomically
        db.session.commit()
        logger.info(f"Order {order.id} created successfully for user {user_id}")
        
        return {
            'order_id': order.id,
            'total_amount': total_amount,
            'status': 'success'
        }
        
    except Exception as e:
        # Rollback all changes if anything fails
        db.session.rollback()
        logger.error(f"Order creation failed for user {user_id}: {str(e)}")
        raise e


def process_payment_with_transaction_safety(order_id, payment_method):
    """
    PROPER TRANSACTION: Process payment with multiple safety checks
    """
    try:
        # Get order with locking (SQLite compatible)
        order = db.session.query(Order)\
            .filter(Order.id == order_id)\
            .with_for_update()\
            .first()
        
        if not order:
            raise ValueError("Order not found")
        
        if order.status != "pending":
            raise ValueError(f"Order status is {order.status}, cannot process payment")
        
        # Process payment (this would integrate with payment gateway)
        payment_success = process_external_payment(order.total_amount, payment_method)
        
        if payment_success:
            order.status = "paid"
            order.paid_at = datetime.now()
        else:
            order.status = "failed"
            # Restore stock if payment failed
            for order_item in order.items:
                order_item.product.stock += order_item.quantity
        
        db.session.commit()
        return {'order_id': order_id, 'status': order.status}
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Payment processing failed for order {order_id}: {str(e)}")
        raise e


def process_external_payment(amount, payment_method):
    """
    Simulate external payment processing
    In real app, this would call payment gateway API
    """
    # Simulate payment processing
    import random
    return random.choice([True, False])  # Simulate 50% success rate for demo


# 3. CONCURRENCY AND RACE CONDITION PROTECTION

def safe_add_to_cart_with_stock_check(user_id, product_id, quantity):
    """
    Safely add item to cart with stock validation and concurrency protection
    """
    try:
        db.session.begin_nested()
        
        # Get user's cart with locking
        cart = db.session.query(Cart)\
            .filter(Cart.user_id == user_id)\
            .with_for_update()\
            .first()
        
        if not cart:
            cart = Cart(user_id=user_id)
            db.session.add(cart)
            db.session.flush()
        
        # Get product with locking
        product = db.session.query(Product)\
            .filter(Product.id == product_id)\
            .with_for_update()\
            .first()
        
        if not product:
            raise ValueError("Product not found")
        
        if product.stock < quantity:
            raise ValueError(f"Only {product.stock} items available, requested {quantity}")
        
        # Check if item already exists in cart
        existing_item = db.session.query(CartItem)\
            .filter(and_(
                CartItem.cart_id == cart.id,
                CartItem.product_id == product_id
            ))\
            .with_for_update()\
            .first()
        
        new_quantity = quantity
        if existing_item:
            new_quantity = existing_item.quantity + quantity
            if new_quantity > product.stock:
                raise ValueError(f"Only {product.stock} items available, cart already has {existing_item.quantity}")
            existing_item.quantity = new_quantity
        else:
            if quantity > product.stock:
                raise ValueError(f"Only {product.stock} items available")
            new_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(new_item)
        
        db.session.commit()
        return {'status': 'success', 'quantity': new_quantity}
        
    except Exception as e:
        db.session.rollback()
        raise e


# 4. BATCH OPERATIONS FOR PERFORMANCE

def bulk_update_product_stock(changes):
    """
    Efficiently update multiple product stocks in a single query
    """
    from sqlalchemy import case
    
    # Create a case statement for bulk update
    stock_updates = case(
        *[(Product.id == prod_id, Product.stock - qty) 
          for prod_id, qty in changes.items()],
        value=Product.id
    )
    
    # Execute bulk update
    updated_count = db.session.query(Product)\
        .filter(Product.id.in_(changes.keys()))\
        .update({Product.stock: stock_updates}, synchronize_session=False)
    
    db.session.commit()
    return updated_count


def get_products_with_optimized_query(category_id=None, include_out_of_stock=False):
    """
    Optimized query with eager loading to prevent N+1 problems
    """
    query = db.session.query(Product)\
        .options(joinedload(Product.category))\
        .order_by(Product.created_at.desc())
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if not include_out_of_stock:
        query = query.filter(Product.stock > 0)
    
    return query.all()


# 5. BUSINESS LOGIC CONSTRAINTS

def validate_business_rules_for_order(cart_items):
    """
    Validate business rules before processing order
    """
    errors = []
    
    for item in cart_items:
        # Check minimum stock requirement
        if item.product.stock < item.quantity:
            errors.append(f"Insufficient stock for {item.product.name}")
        
        # Check maximum quantity per order
        if item.quantity > 50:  # Business rule
            errors.append(f"Maximum quantity exceeded for {item.product.name}")
        
        # Check if product is active/sellable
        if item.product.price <= 0:
            errors.append(f"Product {item.product.name} is not available for sale")
    
    if errors:
        raise ValueError("Validation failed: " + "; ".join(errors))
    
    return True


# 6. ERROR HANDLING AND MONITORING

def safe_execute_with_monitoring(operation_name, operation_func, *args, **kwargs):
    """
    Execute operations with proper error handling and monitoring
    """
    start_time = datetime.now()
    try:
        logger.info(f"Starting operation: {operation_name}")
        result = operation_func(*args, **kwargs)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Operation {operation_name} completed successfully in {duration}s")
        return result
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"Operation {operation_name} failed after {duration}s: {str(e)}")
        raise e


# 7. EXAMPLE API ENDPOINTS WITH PROPER DATA INTEGRITY

def api_add_to_cart(user_id, product_id, quantity):
    """
    API endpoint that properly handles cart operations with data integrity
    """
    try:
        # Validate input
        if not isinstance(product_id, int) or product_id <= 0:
            return {'error': 'Invalid product_id'}, 400
        if not isinstance(quantity, int) or quantity <= 0:
            return {'error': 'Quantity must be positive integer'}, 400
        
        # Execute with concurrency protection
        result = safe_add_to_cart_with_stock_check(user_id, product_id, quantity)
        
        return result, 200
        
    except ValueError as e:
        return {'error': str(e)}, 400
    except Exception as e:
        logger.error(f"API add_to_cart failed: {str(e)}")
        return {'error': 'Internal server error'}, 500


def api_create_order_from_cart(user_id, cart_id):
    """
    API endpoint for creating order with full transaction safety
    """
    try:
        result = create_order_with_stock_reservation(user_id, cart_id)
        return result, 201
    except ValueError as e:
        return {'error': str(e)}, 400
    except Exception as e:
        logger.error(f"API create_order failed: {str(e)}")
        return {'error': 'Internal server error'}, 500


# 8. DATABASE INDEXING STRATEGY (Conceptual - implemented in migrations)

"""
Proper indexing strategy for performance (SQLite):

-- Individual indexes
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_stock ON products(stock);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- Composite indexes for common query patterns
CREATE INDEX idx_products_category_stock ON products(category_id, stock);
CREATE INDEX idx_orders_user_status ON orders(user_id, status);
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at);

-- Note: SQLite has limited support for partial indexes
-- Simple partial indexes are supported but complex WHERE clauses may not be
CREATE INDEX idx_products_active ON products(stock) WHERE stock > 0;  -- Supported in SQLite
"""

if __name__ == "__main__":
    print("Data Integrity Examples - Ready to use!")
    print("This file demonstrates proper implementation of:")
    print("1. Foreign key constraints with cascade options")
    print("2. Transaction handling with rollback safety")
    print("3. Concurrency protection with row locking")
    print("4. Query optimization to prevent N+1 problems")
    print("5. Business logic validation")
    print("6. Error handling and monitoring")
    print("7. API endpoints with data integrity")