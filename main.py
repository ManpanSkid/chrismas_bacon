import logging
import os

import stripe
from starlette.middleware.cors import CORSMiddleware

import in_memory
from db import database, order_service
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from pathlib import Path

from models import OrderIn, Order, PaymentMethod
from payments import stripe_payment, paypal_payment
from payments.helper import complete_payment

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

logging.basicConfig(
    filename='payment.log',
    filemode="w",
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://deinweihnachstbaum.de",
        "https://www.deinweihnachstbaum.de",
        "https://api.deinweihnachstbaum.de",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
database.init_db()

@app.post("/checkout")
async def create_checkout_session(order_in: OrderIn):
    order = Order.from_order_in(order_in)
    order.price = round(order.price, 2)
    logging.info(f"checkout session created by {order.customer.email}, price: {order.price}")
    checkout_url = os.getenv("SUCCESS_URL")

    if order.payment_method == PaymentMethod.Stripe:
        checkout_session = await stripe_payment.create_checkout(order)
        checkout_url = checkout_session.url
    elif order.payment_method == PaymentMethod.Paypal:
        return "Not implemented"
    else:
        in_memory.new_order(order)
        await complete_payment(order.id)

    return {
        "order_id": order.id,
        "price": order.price,
        "checkout_url": checkout_url
    }

@app.get("/orders")
async def get_orders():
    return order_service.get_all_orders()

@app.get("/orders/{order_id:path}")
async def get_order(order_id: str):
    return order_service.get_order(order_id)


@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    return await stripe_payment.stripe_webhook(request)

# @app.post("/paypal/webhook")
# async def stripe_webhook(request: Request):
#     return await paypal_payment.paypal_webhook(request)
