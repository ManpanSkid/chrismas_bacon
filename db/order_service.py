from fastapi import HTTPException
from datetime import datetime
import uuid
from typing import List
import logging

from db.database import get_db
from db.schema import OrderDB
from models import Order, Customer, Tree, Size, Package, Delivery, PaymentMethod

logger = logging.getLogger(__name__)


def create_order(order: Order) -> OrderDB:
    """Create a new order"""
    logger.info("Creating new order")
    try:
        with get_db() as db:
            db_order = OrderDB(
                id=order.id,
                order_date=datetime.now(),
                price=order.price,
                first_name=order.customer.first_name,
                last_name=order.customer.last_name,
                address=order.customer.address,
                postal_code=order.customer.postal_code,
                city=order.customer.city,
                phone=order.customer.phone,
                email=str(order.customer.email),
                tree=order.tree.value,
                size=order.size.value,
                package=order.package.value,
                delivery=order.delivery.value,
                tree_stand=order.tree_stand,
                payment_method=order.payment_method.value
            )

            db.add(db_order)
            db.commit()
            db.refresh(db_order)

            logger.info(f"Order created successfully: {order.id} for customer {order.customer.email}")
            return db_order

    except Exception as e:
        logger.error(f"Failed to create order: {str(e)}", exc_info=True)
        raise


def get_all_orders() -> List[OrderDB]:
    """Get all orders"""
    logger.info("Fetching all orders")
    try:
        with get_db() as db:
            orders = db.query(OrderDB).all()
            logger.info(f"Retrieved {len(orders)} order/s")
            return [o for o in orders]

    except Exception as e:
        logger.error(f"Failed to fetch orders: {str(e)}", exc_info=True)
        raise


def get_order(order_id: str) -> OrderDB:
    """Get a specific order by ID"""
    logger.info(f"Fetching order: {order_id}")
    try:
        with get_db() as db:
            order = db.query(OrderDB).filter(OrderDB.id == order_id).first()
            if not order:
                order = db.query(OrderDB).filter(OrderDB.email == order_id).first()

            if not order:
                logger.warning(f"Order not found: {order_id}")
                raise HTTPException(status_code=404, detail="Order not found")

            logger.info(f"Order retrieved successfully: {order_id}")
            return order

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch order {order_id}: {str(e)}", exc_info=True)
        raise


def delete_order(order_id: str) -> dict:
    """Delete an order by ID"""
    logger.info(f"Deleting order: {order_id}")
    try:
        with get_db() as db:
            order = db.query(OrderDB).filter(OrderDB.id == order_id).first()
            if not order:
                logger.warning(f"Order not found for deletion: {order_id}")
                raise HTTPException(status_code=404, detail="Order not found")

            db.delete(order)
            db.commit()

            logger.info(f"Order deleted successfully: {order_id}")
            return {"message": "Order deleted successfully", "order_id": order_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete order {order_id}: {str(e)}", exc_info=True)
        raise