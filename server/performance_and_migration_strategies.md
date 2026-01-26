# Indexing, Query Optimization & Migration Strategies

This document covers the critical concepts of database performance optimization and safe migration strategies using your ecommerce project as examples.

## 1. Database Indexing Strategy

### Understanding Index Types

#### Single Column Indexes

```sql
-- For frequently queried columns
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_products_price ON products(price);
```

#### Composite Indexes

```sql
-- For common multi-column queries
CREATE INDEX idx_products_category_price ON products(category_id, price);
CREATE INDEX idx_orders_user_status ON orders(user_id, status);
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at DESC);
```

#### Partial Indexes (Limited in SQLite)

```sql
-- SQLite has limited support for partial indexes compared to PostgreSQL
-- For filtered queries (SQLite supports simple partial indexes)
-- Note: Complex WHERE clauses may not be supported in all SQLite versions
CREATE INDEX idx_products_in_stock ON products(stock) WHERE stock > 0;
-- For more complex filtering, use regular indexes and application logic
CREATE INDEX idx_orders_status ON orders(status);  -- Use this with app logic instead of partial index
```

### Adding Indexes to Models

In your models.py, you can specify indexes using `__table_args__`:

```python
class Product(db.Model, SerializerMixin):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)  # Single column index
    price = db.Column(db.Float, nullable=False, index=True)
    stock = db.Column(db.Integer, default=0, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), index=True)

    # Composite index for common query patterns
    __table_args__ = (
        db.Index('idx_category_price', 'category_id', 'price'),  # For category + price filtering
        db.Index('idx_name_text', 'name'),  # For text search (SQLite)
        # Partial index condition (requires raw SQL in migration)
    )
```

## 2. Query Optimization Techniques

### AVOIDING N+1 Queries

**BAD - N+1 Query Problem:**

```python
def get_products_with_categories_bad():
    # 1 query to get products
    products = Product.query.all()

    result = []
    # N additional queries to get each category
    for product in products:
        result.append({
            'name': product.name,
            'category': product.category.name  # <-- Triggers separate query!
        })
    return result
```

**GOOD - Eager Loading:**

```python
from sqlalchemy.orm import joinedload, selectinload

def get_products_with_categories_good():
    # Single query with JOIN to get products and categories
    products = Product.query.options(joinedload(Product.category)).all()

    result = []
    for product in products:
        result.append({
            'name': product.name,
            'category': product.category.name  # <-- No additional query needed
        })
    return result

# Alternative with selectinload (better for collections)
def get_orders_with_items():
    orders = Order.query.options(selectinload(Order.items)).all()
    return orders
```

### Query Profiling and Analysis

```python
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time

# Query profiler for development
@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    if total > 0.1:  # Log queries taking more than 100ms
        print(f"SLOW QUERY ({total:.3f}s): {statement[:100]}...")
```

### Pagination for Large Datasets

```python
def get_paginated_products(page=1, per_page=20, category_id=None):
    query = Product.query

    if category_id:
        query = query.filter(Product.category_id == category_id)

    # Use paginate to avoid loading all records into memory
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False  # Don't throw error for invalid page
    )

    return {
        'items': [product.to_dict() for product in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }
```

## 3. Advanced Query Optimization

### Raw SQL for Complex Queries

```python
def get_product_sales_report():
    """
    Complex report query using raw SQL for better performance
    """
    sql = '''
    SELECT
        p.name,
        p.stock,
        COALESCE(SUM(oi.quantity), 0) as total_sold,
        COALESCE(SUM(oi.quantity * oi.price), 0) as total_revenue
    FROM products p
    LEFT JOIN order_items oi ON p.id = oi.product_id
    LEFT JOIN orders o ON oi.order_id = o.id AND o.status = 'paid'
    GROUP BY p.id, p.name, p.stock
    ORDER BY total_revenue DESC
    LIMIT 50
    '''

    result = db.session.execute(sql)
    return [dict(row) for row in result.fetchall()]
```

### Query with Subqueries

```python
from sqlalchemy import func, desc

def get_top_products_by_category():
    """
    Get top selling products in each category
    """
    # Subquery to calculate sales rank within each category
    ranked_products = db.session.query(
        Product,
        Category.name.label('category_name'),
        func.rank().over(
            partition_by=Product.category_id,
            order_by=func.coalesce(
                db.session.query(func.sum(OrderItem.quantity))
                .filter(OrderItem.product_id == Product.id)
                .filter(OrderItem.order.has(Order.status == 'paid'))
                .as_scalar(),
                0
            ).desc()
        ).label('rank')
    ).join(Category).subquery()

    # Filter to get top 3 in each category
    top_products = db.session.query(ranked_products).filter(
        ranked_products.c.rank <= 3
    ).order_by(ranked_products.c.category_name, ranked_products.c.rank)

    return top_products.all()
```

## 4. Migration Strategies

### Zero-Downtime Migration Patterns

#### Add Column Pattern (Safe)

```python
"""Add new column with safe migration

Revision ID: abc123newcol
Revises: previous_revision_id
Create Date: 2026-01-12 23:00:00

"""
from alembic import op
import sqlalchemy as sa


revision = 'abc123newcol'
down_revision = 'previous_revision_id'
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Add column as nullable
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('weight_kg', sa.Float(), nullable=True))

    # Step 2: Populate with default values (optional)
    connection = op.get_bind()
    connection.execute(
        "UPDATE products SET weight_kg = 0.0 WHERE weight_kg IS NULL"
    )

    # Step 3: Make column non-nullable after populating
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.alter_column('weight_kg', nullable=False)


def downgrade():
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_column('weight_kg')
```

#### Rename Column Pattern (Safe)

```python
"""Rename column with compatibility

Revision ID: rename_col_safe
Revises: abc123newcol
Create Date: 2026-01-12 23:15:00

"""
from alembic import op
import sqlalchemy as sa


revision = 'rename_col_safe'
down_revision = 'abc123newcol'
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Add new column with desired name
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('display_name', sa.String(150), nullable=True))

    # Step 2: Copy data from old column to new column
    connection = op.get_bind()
    connection.execute(
        "UPDATE products SET display_name = name WHERE display_name IS NULL"
    )

    # Step 3: Make new column non-nullable
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.alter_column('display_name', nullable=False)

    # Step 4: Update application code to use new column
    # (Deploy new code that uses display_name instead of name)

    # Step 5: Drop old column (in separate migration after confidence)
    # with op.batch_alter_table('products', schema=None) as batch_op:
    #     batch_op.drop_column('name')


def downgrade():
    # Reverse the process
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_column('display_name')
```

### Schema Change with Data Migration

```python
"""Migrate user roles to new enum values

Revision ID: migrate_roles_enum
Revises: rename_col_safe
Create Date: 2026-01-12 23:30:00

"""
from alembic import op
import sqlalchemy as sa


revision = 'migrate_roles_enum'
down_revision = 'rename_col_safe'
branch_labels = None
depends_on = None


def upgrade():
    # Create new enum type
    new_role_enum = sa.Enum('CUSTOMER', 'ADMIN', 'MODERATOR', name='user_roles_new')
    new_role_enum.create(op.get_bind())

    # Add new temporary column with new enum
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role_new', new_role_enum, nullable=True))

    # Migrate data (convert old values to new values)
    connection = op.get_bind()
    connection.execute(
        "UPDATE users SET role_new = 'ADMIN' WHERE role = 'admin'"
    )
    connection.execute(
        "UPDATE users SET role_new = 'CUSTOMER' WHERE role = 'customer'"
    )
    connection.execute(
        "UPDATE users SET role_new = 'CUSTOMER' WHERE role IS NULL OR role = ''"
    )

    # Make new column non-nullable and drop old column
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('role_new', nullable=False)
        batch_op.drop_column('role')
        batch_op.alter_column('role_new', new_column_name='role')

    # Drop old enum type if it existed
    old_role_enum = sa.Enum(name='user_roles_old')
    old_role_enum.drop(op.get_bind(), checkfirst=True)


def downgrade():
    # Reverse migration
    pass
```

## 5. Performance Monitoring

### Query Execution Plan Analysis

```python
def analyze_query_performance():
    """
    Function to analyze and optimize slow queries
    """
    from sqlalchemy import text

    # Example: Analyze a potentially slow query (SQLite uses EXPLAIN QUERY PLAN)
    query_plan = db.session.execute(
        text("EXPLAIN QUERY PLAN SELECT * FROM products WHERE category_id = 1 AND price < 100")
    )

    plan_rows = query_plan.fetchall()
    print("Query Execution Plan:")
    for row in plan_rows:
        print(row[0] if row and len(row) > 0 else "No plan available")

    # Look for:
    # - SCAN (should be SEARCH when indexed)
    # - SEARCH with proper index usage
    # - Missing indexes indicated by full table scans
```

### Database Connection Pooling

```python
# In app.py configuration
app.config.update(
    SQLALCHEMY_ENGINE_OPTIONS={
        'pool_size': 10,  # Number of connections to maintain
        'max_overflow': 20,  # Additional connections beyond pool_size
        'pool_timeout': 30,  # Seconds to wait before giving up on connection
        'pool_recycle': 3600,  # Recycle connections after 1 hour
        'pool_pre_ping': True,  # Validate connections before use
    }
)
```

## 6. Frontend Integration Considerations

### API Response Optimization

```python
def get_optimized_product_list(filters=None, page=1, per_page=20):
    """
    Optimized API endpoint that minimizes database queries
    """
    query = db.session.query(Product.id, Product.name, Product.price, Product.image_url)\
        .options(joinedload(Product.category))

    # Apply filters efficiently
    if filters and 'category_id' in filters:
        query = query.filter(Product.category_id == filters['category_id'])
    if filters and 'min_price' in filters:
        query = query.filter(Product.price >= filters['min_price'])
    if filters and 'max_price' in filters:
        query = query.filter(Product.price <= filters['max_price'])

    # Pagination to avoid huge responses
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # Prepare response with minimal data transfer
    response = {
        'products': [
            {
                'id': p.id,
                'name': p.name,
                'price': float(p.price),
                'image_url': p.image_url,
                'category': p.category.name if p.category else None
            }
            for p in pagination.items
        ],
        'pagination': {
            'current_page': pagination.page,
            'total_pages': pagination.pages,
            'total_items': pagination.total,
            'per_page': per_page
        }
    }

    return response
```

### Caching Strategies

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/products')
@cache.cached(timeout=300, query_string=True)  # Cache for 5 minutes, vary by query params
def cached_products():
    # Expensive query that benefits from caching
    products = get_optimized_product_list(request.args)
    return jsonify(products)
```

## 7. Monitoring and Alerting

### Slow Query Detection

```python
import logging
from functools import wraps

def monitor_slow_queries(threshold=0.5):  # 500ms threshold
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time

            if duration > threshold:
                logging.warning(f"SLOW QUERY in {func.__name__}: {duration:.3f}s")
                # Could send to monitoring service like Sentry, DataDog, etc.

            return result
        return wrapper
    return decorator

@monitor_slow_queries(threshold=0.5)
def slow_database_operation():
    # Your database operation here
    pass
```

## 8. Migration Best Practices Checklist

### Pre-Migration Checklist

- [ ] Test migration on staging environment
- [ ] Backup database before migration
- [ ] Ensure migration can be rolled back
- [ ] Check for dependent services/queries
- [ ] Plan for zero-downtime deployment
- [ ] Monitor application after migration

### Post-Migration Checklist

- [ ] Verify data integrity
- [ ] Test all affected functionality
- [ ] Monitor application performance
- [ ] Clean up temporary columns/indexes if needed
- [ ] Update documentation

Remember: Performance optimization is an ongoing process. Regularly monitor your application, analyze slow queries, and optimize based on actual usage patterns rather than premature optimization.
