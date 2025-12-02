import uuid
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, EmailStr


class Tree(Enum):
    Nordmann = "nordmann"


class Size(Enum):
    Small = "s"
    Medium = "m"
    Large = "l"
    XLarge = "xl"


class Package(Enum):
    Basic = "basic"
    Extra = "extra"
    Full = "full"


class Delivery(Enum):
    Standard = "standard"
    Fast = "fast"
    Express = "express"


class PaymentMethod(Enum):
    Stripe = "stripe"
    Paypal = "paypal"
    Cash = "cash"


class Customer(BaseModel):
    first_name: str
    last_name: str
    address: str
    postal_code: str
    city: str
    phone: str
    email: EmailStr


class OrderIn(BaseModel):
    customer: Customer
    tree: Tree
    size: Size
    package: Package
    delivery: Delivery
    tree_stand: bool
    payment_method: PaymentMethod

priceList = {
    Tree.Nordmann: 1,

    Size.Small: 35.87,
    Size.Medium: 49.92,
    Size.Large: 65.76,
    Size.XLarge: 79.89,

    Package.Basic: 33.23,
    Package.Extra: 41.36,
    Package.Full: 55.78,

    Delivery.Standard: 0,
    Delivery.Fast: 8.85,
    Delivery.Express: 24.67,

    "treeStand": 35.99
}

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer: Customer
    tree: Tree
    size: Size
    package: Package
    delivery: Delivery
    tree_stand: bool
    order_date: datetime = Field(default_factory=datetime.now)
    price: float
    payment_method: PaymentMethod

    @classmethod
    def from_order_in(cls, order_in: OrderIn) -> "Order":
        price = cls.calculate_price(
            tree=order_in.tree,
            size=order_in.size,
            package=order_in.package,
            delivery=order_in.delivery,
            tree_stand=order_in.tree_stand
        )

        return cls(
            customer=order_in.customer,
            tree=order_in.tree,
            size=order_in.size,
            package=order_in.package,
            delivery=order_in.delivery,
            tree_stand=order_in.tree_stand,
            price=price,
            payment_method=order_in.payment_method
        )

    @staticmethod
    def calculate_price(tree: Tree, size: Size, package: Package,
                        delivery: Delivery, tree_stand: bool) -> float:
        tree_multiplier = priceList[tree]

        size_price = priceList[size] * tree_multiplier
        package_price = priceList[package]
        delivery_price = priceList[delivery]
        tree_stand_price = priceList["treeStand"] if tree_stand else 0

        return size_price + package_price + delivery_price + tree_stand_price
