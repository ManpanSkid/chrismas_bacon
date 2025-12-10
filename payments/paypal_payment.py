import logging
import os
from fastapi import Request, HTTPException
import paypalrestsdk
from paypalrestsdk.notifications import WebhookEvent

import in_memory
from payments.helper import complete_payment

logger = logging.getLogger(__name__)


async def create_checkout(order):
    paypalrestsdk.configure({
        "mode": os.getenv("PAYPAL_MODE", "sandbox"),  # sandbox or live
        "client_id": os.getenv("PAYPAL_CLIENT_ID"),
        "client_secret": os.getenv("PAYPAL_CLIENT_SECRET")
    })

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": os.getenv("SUCCESS_URL"),
            "cancel_url": os.getenv("CANCEL_URL")
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "FastAPI PayPal Checkout",
                    "sku": "item",
                    "price": f"{order.price:.2f}",
                    "currency": "EUR",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": f"{order.price:.2f}",
                "currency": "EUR"
            },
            "description": "FastAPI PayPal Checkout",
            "custom": order.id,  # Store order ID in custom field
            "invoice_number": order.id
        }],
        "note_to_payer": f"Customer email: {order.customer.email}"
    })

    if payment.create():
        in_memory.new_order(order)
        # Return approval URL for redirect
        for link in payment.links:
            if link.rel == "approval_url":
                return {"url": link.href, "payment_id": payment.id}
    else:
        logging.error(f"PayPal payment creation error: {payment.error}")
        raise HTTPException(status_code=400, detail=payment.error)


async def stripe_webhook(request: Request):
    # Configure PayPal SDK
    paypalrestsdk.configure({
        "mode": os.getenv("PAYPAL_MODE", "sandbox"),
        "client_id": os.getenv("PAYPAL_CLIENT_ID"),
        "client_secret": os.getenv("PAYPAL_CLIENT_SECRET")
    })

    payload = await request.body()

    # Get webhook headers
    transmission_id = request.headers.get("PAYPAL-TRANSMISSION-ID")
    transmission_time = request.headers.get("PAYPAL-TRANSMISSION-TIME")
    cert_url = request.headers.get("PAYPAL-CERT-URL")
    auth_algo = request.headers.get("PAYPAL-AUTH-ALGO")
    transmission_sig = request.headers.get("PAYPAL-TRANSMISSION-SIG")
    webhook_id = os.getenv("PAYPAL_WEBHOOK_ID")

    if not all([transmission_id, transmission_time, cert_url, auth_algo, transmission_sig, webhook_id]):
        logging.error("Missing PayPal webhook headers")
        raise HTTPException(status_code=400, detail="Missing webhook headers")

    try:
        # Verify webhook signature using PayPal SDK
        webhook_event = WebhookEvent.verify(
            transmission_id=transmission_id,
            timestamp=transmission_time,
            webhook_id=webhook_id,
            event_body=payload.decode('utf-8'),
            cert_url=cert_url,
            actual_signature=transmission_sig,
            auth_algo=auth_algo
        )

        # If verification successful, webhook_event will contain the verified event
        event_type = webhook_event.get("event_type")
        print("event_type", event_type)

        if event_type == "PAYMENT.SALE.COMPLETED":
            logging.info("Received payment sale completed")

            # Retrieve resource and custom data
            resource = webhook_event.get("resource", {})

            # Get order ID from custom field or invoice_number
            order_id = resource.get("custom") or resource.get("invoice_number")

            if not order_id:
                logging.error("Invalid metadata checkout")
                raise HTTPException(status_code=400, detail="Missing order ID")

            complete_payment(order_id)

        return {"status": "success"}

    except paypalrestsdk.exceptions.UnauthorizedAccess as e:
        logging.error(f"PayPal webhook signature verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid signature")
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))