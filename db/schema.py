from sqlalchemy import Column, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class OrderDB(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, index=True)  # UUID-style
    order_date = Column(DateTime(timezone=True), server_default=func.now())
    price = Column(Float, nullable=False)

    # Customer info
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    postal_code = Column(String(20), nullable=False)
    city = Column(String(100), nullable=False)
    phone = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False)

    # Order details
    tree = Column(String(100), nullable=False)
    size = Column(String(50), nullable=False)
    package = Column(String(100), nullable=False)
    delivery = Column(String(50), nullable=False)
    tree_stand = Column(Boolean, nullable=False)
    payment_method = Column(String(50), nullable=False)
    status = Column(String(50), default="eingegangen")
