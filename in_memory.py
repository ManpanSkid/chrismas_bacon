import uuid
from datetime import datetime
from models import Order, Customer, Tree, Size, Package, Delivery, PaymentMethod

open_orders = {}

def get_order(order_id: str) -> Order:
    """Get an order by its UUID"""
    return open_orders[order_id]

def delete_order(order_id: str):
    """Delete an order by its UUID"""
    del open_orders[order_id]

def new_order(order_in: Order):
    """Add a new order to the memory"""
    open_orders[order_in.id] = order_in
