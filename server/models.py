from extensions import db, bcrypt  # Use extensions instead of redefining
from sqlalchemy.orm import validates, relationship
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
import re


# USER MODEL
class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False, index=True)  # Added index
    last_name = db.Column(db.String(50), nullable=False, index=True)   # Added index
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)  # Added index
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="customer", index=True)  # Added index
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)  # Added index
    phone_number = db.Column(db.String(20), unique=True, nullable=False, index=True)  # Added index
    carts = relationship("Cart", back_populates="user")
    orders = relationship("Order", back_populates="user")

    serialize_rules = ('-password_hash', '-carts.user', '-orders.user')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def set_password(self, raw_password):
        self.password_hash = bcrypt.generate_password_hash(raw_password).decode('utf-8')

    def verify_password(self, raw_password):
        return bcrypt.check_password_hash(self.password_hash, raw_password)

    @validates("email")
    def validate_email(self, key, value):
        value = value.strip().lower()
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", value):
            raise ValueError("Invalid email")
        return value
    
    @validates("phone_number")
    def validate_phone(self, key, value):
        if value and not re.match(r"^\+?\d{7,15}$", value):
            raise ValueError("Invalid phone number format")
        return value

# CATEGORY MODEL
class Category(db.Model, SerializerMixin):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)  # Added index
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)  # Added index

    products = relationship("Product", back_populates="category")
    serialize_rules = ('-products.category',)
    

# PRODUCT MODEL
class Product(db.Model, SerializerMixin):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)  # Added index
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False, index=True)  # Added index
    stock = db.Column(db.Integer, default=0, index=True)  # Added index
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)  # Added index
    image_url = db.Column(db.String)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), index=True)  # Added index
    category = relationship("Category", back_populates="products")

    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")

    serialize_rules = ('-cart_items.product', '-order_items.product', '-category.products')
    
    # Composite index for common queries
    __table_args__ = (
        db.Index('idx_product_category_stock', 'category_id', 'stock'),  # For category + stock queries
        db.Index('idx_product_category_price', 'category_id', 'price'),   # For category + price queries
    )


    @validates("price")
    def validate_price(self, key, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError("Price must be a valid number")

        if value < 0:
            raise ValueError("Price must be a positive number")
        return value


    @validates("stock")
    def validate_stock(self, key, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValueError("Stock must be a valid integer")

        if value < 0:
            raise ValueError("Stock must be a positive integer")
        return value

   
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "stock": self.stock,
            "image_url": self.image_url,
            "category": {
                "id": self.category.id,
                "name": self.category.name
            } if self.category else None,
            
        }

# CART MODEL
class Cart(db.Model, SerializerMixin):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)  # Added index
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)  # Added index

    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

    serialize_rules = ("-items.cart",)
    
    # Index for user_id commonly used in queries
    __table_args__ = (
        db.Index('idx_cart_user_created', 'user_id', 'created_at'),  # For user's cart history
    )


class CartItem(db.Model, SerializerMixin):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False, index=True)  # Added index
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)  # Added index
    quantity = db.Column(db.Integer, default=1, index=True)  # Added index

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")

    serialize_rules = ("-cart.items", "-product.cart_items")
    
    # Composite index for common queries
    __table_args__ = (
        db.Index('idx_cart item_cart_product', 'cart_id', 'product_id'),  # For cart item uniqueness
    )

# ORDER MODEL
class Order(db.Model, SerializerMixin):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)  # Added index
    total_amount = db.Column(db.Float, nullable=False, index=True)  # Added index
    status = db.Column(db.String(20), default="pending", index=True)  # Added index
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)  # Added index
    mpesa_checkout_request_id = db.Column(db.String(100), index=True)  # Added index for M-Pesa integration
    paid_at = db.Column(db.DateTime, index=True)  # Added for tracking payment time

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    # Composite indexes for common queries
    __table_args__ = (
        db.Index('idx_order_user_status', 'user_id', 'status'),  # For user orders by status
        db.Index('idx_order_user_created', 'user_id', 'created_at'),  # For user order history
        db.Index('idx_order_status_created', 'status', 'created_at'),  # For orders by status and date
        db.Index('idx_orders_paid_at', 'paid_at'),  # For payment date queries
    )


class OrderItem(db.Model, SerializerMixin):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)  # Added index
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)  # Added index
    quantity = db.Column(db.Integer, default=1, index=True)  # Added index
    price = db.Column(db.Float, nullable=False, index=True)  # Added index

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    
    # Composite index for common queries
    __table_args__ = (
        db.Index('idx_orderitem_order_product', 'order_id', 'product_id'),  # For order items uniqueness
    )
