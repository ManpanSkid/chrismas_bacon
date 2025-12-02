# db/schema.py
from sqlalchemy import Column, String, Float, DateTime, create_engine, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class OrderDB(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True)
    order_date = Column(DateTime, default=datetime.now)
    price = Column(Float, nullable=False)

    # Customer info
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    city = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)

    # Order details
    tree = Column(String, nullable=False)
    size = Column(String, nullable=False)
    package = Column(String, nullable=False)
    delivery = Column(String, nullable=False)
    tree_stand = Column(Boolean, nullable=False)
    payment_method = Column(String, nullable=False)
    status = Column(String, default='eingegangen')