import uuid
from datetime import datetime
from models import Order, Customer, Tree, Size, Package, Delivery, PaymentMethod

# Mocking required fields
mock_customer = Customer(
    first_name="John",
    last_name="Doe",
    address="123 Main St",
    postal_code="12345",
    city="Springfield",
    phone="+1234567890",
    email="john.doe@example.com"
)

mock_tree = Tree.Nordmann
mock_size = Size.Medium
mock_package = Package.Basic
mock_delivery = Delivery.Standard
mock_payment_method = PaymentMethod.Stripe

# Create an Order with a fixed UUID
fixed_id = str(uuid.UUID("00000000-0000-0000-0000-000000000001"))
order = Order(
    id=fixed_id,
    customer=mock_customer,
    tree=mock_tree,
    size=mock_size,
    package=mock_package,
    delivery=mock_delivery,
    tree_stand=True,
    price=100.0,
    payment_method=mock_payment_method
)

# Store in open_orders
open_orders = {}

# Functions
def get_order(order_id: str) -> Order:
    """Get an order by its UUID"""
    return open_orders[order_id]

def delete_order(order_id: str):
    """Delete an order by its UUID"""
    del open_orders[order_id]

def new_order(order_in: Order):
    """Add a new order to the memory"""
    open_orders[order_in.id] = order_in

new_order(order)
