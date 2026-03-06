from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from models import db, Product, OrderItem, User
from sqlalchemy.orm import joinedload
from utils.decorators import admin_required

from auth_context import log_user_action
from logging_config import get_logger, log_exception

logger = get_logger('admin.products')

class AdminProductsResource(Resource):
    """
    Admin-only Product Management
    """

    # GET all products ( filter by low stock)
    @admin_required
    def get(self):

        low_stock = request.args.get("low_stock", type=int)
        query = Product.query
        
        # Use joinedload to prevent N+1 queries when accessing related data
        query = query.options(joinedload(Product.category))
        
        if low_stock is not None:
            query = query.filter(Product.stock <= low_stock)

        products = query.all()

        data = []
        for product in products:
            # Optimize aggregate queries by using subqueries instead of separate queries
            # Calculate total sales for this product
            total_sales_result = (
                db.session.query(func.sum(OrderItem.quantity))
                .filter(OrderItem.product_id == product.id)
                .filter(OrderItem.order.has(status='paid'))  # Only count paid orders
                .scalar()
            )
            total_sales = total_sales_result or 0

            # Calculate total revenue for this product
            total_revenue_result = (
                db.session.query(func.sum(OrderItem.price * OrderItem.quantity))
                .filter(OrderItem.product_id == product.id)
                .filter(OrderItem.order.has(status='paid'))  # Only count paid orders
                .scalar()
            )
            total_revenue = total_revenue_result or 0

            product_dict = product.to_dict()
            product_dict.update({
                "total_sales": total_sales,
                "total_revenue": float(total_revenue),
                "low_stock_warning": product.stock <= 5,  # Example business rule
            })
            data.append(product_dict)

        # Log products listed
        logger.info(
            f"Admin {current_user_id} listed {len(data)} products",
            event="products_listed",
            count=len(data),
            low_stock_filter=low_stock is not None
        )

        return {"products": data, "count": len(data)}, 200

    @jwt_required()
    def post(self):
        """Create a new product (admin only)"""
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user or current_user.role != "admin":
            # Log unauthorized attempt
            logger.warning(
                "Non-admin attempted to create product",
                event="unauthorized_admin_access",
                endpoint="create_product",
                role=current_user.role if current_user else None
            )
            return {"error": "Admins only"}, 403

        data = request.get_json()
        if not data:
            return {"error": "No data provided"}, 400

        required_fields = ["name", "price", "stock"]
        for field in required_fields:
            if field not in data:
                return {"error": f"'{field}' is required"}, 400

        try:
            product = Product(
                name=data["name"],
                description=data.get("description", ""),
                price=float(data["price"]),
                stock=int(data["stock"]),
                image_url=data.get("image_url"),
                category_id=data.get("category_id")
            )
            db.session.add(product)
            db.session.commit()
            
            # Log product created
            logger.info(
                f"Product '{product.name}' created by admin",
                event="product_created",
                product_id=product.id,
                product_name=product.name,
                price=product.price,
                stock=product.stock
            )
            
            # Record admin action
            log_user_action('product_created', product_id=product.id)
            
            return {
                "message": "Product created successfully",
                "product": product.to_dict()
            }, 201
        except ValueError as e:
            return {"error": f"Invalid data: {str(e)}"}, 400
        except Exception as e:
            db.session.rollback()
            # Log product creation failure
            log_exception(
                "Failed to create product",
                error=e,
                event="product_operation_failure",
                operation="create"
            )
            return {"error": f"Failed to create product: {str(e)}"}, 500

    @admin_required
    def put(self, product_id):
        """Update an existing product (admin only)"""
        pass  # Admin check handled by decorator

        product = Product.query.get(product_id)
        if not product:
            return {"error": "Product not found"}, 404

        data = request.get_json()
        if not data:
            return {"error": "No data provided"}, 400

        try:
            # Update allowed fields
            updatable_fields = ["name", "description", "price", "stock", "image_url", "category_id"]
            updated_fields = []
            for field in updatable_fields:
                if field in data:
                    setattr(product, field, data[field])
                    updated_fields.append(field)

            db.session.commit()
            
            # Log product updated
            logger.info(
                f"Product {product.id} updated by admin",
                event="product_updated",
                product_id=product.id,
                changed_fields=updated_fields
            )
            
            # Record admin action
            log_user_action('product_updated', product_id=product.id)
            
            return {
                "message": "Product updated successfully",
                "product": product.to_dict()
            }, 200
        except Exception as e:
            db.session.rollback()
            # Log product update failure
            log_exception(
                "Failed to update product",
                error=e,
                event="product_operation_failure",
                operation="update",
                product_id=product_id
            )
            return {"error": f"Failed to update product: {str(e)}"}, 500

    @admin_required
    def delete(self, product_id):
        """Delete a product (admin only) - with validation"""
        pass  # Admin check handled by decorator

        product = Product.query.get(product_id)
        if not product:
            return {"error": "Product not found"}, 404

        # Check if product is referenced in any unpaid orders
        from models import OrderItem, Order
        active_order_items = db.session.query(OrderItem).join(Order)\
            .filter(OrderItem.product_id == product_id)\
            .filter(Order.status.in_(['pending', 'processing']))\
            .count()
        
        if active_order_items > 0:
            # Log deletion blocked
            logger.warning(
                f"Admin attempted to delete product {product_id} with active orders",
                event="product_deletion_blocked",
                product_id=product_id,
                active_order_count=active_order_items
            )
            return {
                "error": f"Cannot delete product. It is referenced in {active_order_items} active orders."
            }, 400

        try:
            db.session.delete(product)
            db.session.commit()
            
            # Log product deleted
            logger.info(
                f"Product '{product.name}' deleted by admin",
                event="product_deleted",
                product_id=product_id,
                product_name=product.name
            )
            
            # Record admin action
            log_user_action('product_deleted', product_id=product_id)
            
            return {"message": "Product deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            # Log product deletion failure
            log_exception(
                "Failed to delete product",
                error=e,
                event="product_operation_failure",
                operation="delete",
                product_id=product_id
            )
            return {"error": f"Failed to delete product: {str(e)}"}, 500