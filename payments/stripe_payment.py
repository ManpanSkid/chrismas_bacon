import logging
import os
import stripe
from fastapi import Request, HTTPException

import in_memory
from payments.helper import complete_payment

logger = logging.getLogger(__name__)

async def create_checkout(order):
    session = stripe.checkout.Session.create(
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {"name": "FastAPI Stripe Checkout"},
                "unit_amount": int(order.price * 100),
            },
            "quantity": 1,
        }],
        metadata={
            "request_id": order.id
        },
        mode="payment",
        success_url=os.getenv("SUCCESS_URL"),
        cancel_url=os.getenv("CANCEL_URL"),
        customer_email=order.customer.email,
    )

    in_memory.new_order(order)
    return session

async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )

    except stripe.error.SignatureVerificationError as e:
        logging.error(f"Invalid signature: {e}")
        raise HTTPException(status_code=400)
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400)

    event_type = event["type"]

    if event_type == "checkout.session.completed":
        logging.info("Received checkout session completed")

        # Retrieve session and metadata if needed
        session = event["data"]["object"]

        metadata = session.get("metadata", {})

        order_id = metadata.get("request_id")
        if not order_id:
            logging.error("Invalid metadata checkout")
            raise HTTPException(status_code=400)

        await complete_payment(order_id)

    return {"status": "success"}