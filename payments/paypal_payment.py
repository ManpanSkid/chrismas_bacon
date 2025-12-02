import json
import logging
import os
import requests
from fastapi import Request, HTTPException
from db import order_service

import in_memory
import smtp
from models import Order
from payments.helper import complete_payment

logger = logging.getLogger(__name__)

def get_paypal_token():
    url = f"{os.getenv("PAYPAL_BASE")}/v1/oauth2/token"
    response = requests.post(
        url,
        auth=(os.getenv("PAYPAL_CLIENT_ID"), os.getenv("PAYPAL_SECRET")),
        data={"grant_type": "client_credentials"}
    )
    return response.json()["access_token"]


def verify_webhook_signature(headers, body):
    validate_url = f"{os.getenv("PAYPAL_BASE")}/v1/notifications/verify-webhook-signature"
    token = get_paypal_token()

    data = {
        "auth_algo": headers.get("paypal-auth-algo"),
        "cert_url": headers.get("paypal-cert-url"),
        "transmission_id": headers.get("paypal-transmission-id"),
        "transmission_sig": headers.get("paypal-transmission-sig"),
        "transmission_time": headers.get("paypal-transmission-time"),
        "webhook_id": "YOUR_WEBHOOK_ID",  # From PayPal dashboard
        "webhook_event": json.loads(body)
    }

    response = requests.post(
        validate_url,
        json=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )

    status = response.json().get("verification_status")
    return status == "SUCCESS"


def create_order(order: Order):
    token = get_paypal_token()
    url = f"{os.getenv("PAYPAL_BASE")}/v2/checkout/orders"

    payload = {
        "request_id": order.id,
        "purchase_units": [
            {
                "amount": {"currency_code": "EUR", "value": order.price}
            }
        ],
        "application_context": {
            "brand_name": "Dein Weihnachtsbaum",
            "return_url": "https://your-domain.com/paypal/success",
            "cancel_url": "https://your-domain.com/paypal/cancel",
        }
    }

    response = requests.post(
        url,
        json=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )

    json_response = response.json()

    # find approval link
    for link in order["links"]:
        if link["rel"] == "approve":
            return link["href"]

    return "No approve link found"


async def paypal_webhook(request: Request):
    raw_body = await request.body()
    body_str = raw_body.decode("utf-8")
    headers = request.headers

    # 1. VERIFY SIGNATURE
    if not verify_webhook_signature(headers, body_str):
        raise HTTPException(status_code=400, detail="Invalid signature")

    event = json.loads(body_str)
    event_type = event["event_type"]
    resource = event["resource"]

    print("Received PayPal Event:", event_type)

    # 2. HANDLE PAYMENT COMPLETED EVENTS
    if event_type == "CHECKOUT.ORDER.APPROVED":
        order_id = resource["id"]
        print("Order approved:", order_id)

    if event_type == "PAYMENT.CAPTURE.COMPLETED":
        logging.info("Received checkout session completed")

        capture = resource
        order_id = capture["request_id"]
        amount = capture["amount"]["value"]

        print("Payment completed for order:", order_id)
        print("Amount:", amount)

        complete_payment(order_id)

    return {"status": "ok"}
