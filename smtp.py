import logging
import os
import smtplib
from email.message import EmailMessage

from models import Order


def send_email(to_address: str, subject: str, body: str):
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", 587))
    user = os.getenv("SMTP_INFO")
    password = os.getenv("SMTP_INFO_PW")

    try:
        msg = EmailMessage()
        msg["From"] = user
        msg["To"] = to_address
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP(host, port) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(user, password)
            smtp.send_message(msg)

    except Exception as e:
        logging.error(f"Email send failed: {e}")


def send_new_order_received_admin(order: Order):
    admin_email = os.getenv("SMTP_USER")

    subject = "New Order Received"
    body = (
        f"A new order has been placed.\n\n"
        f"Order ID: {order.id}\n"
        f"Customer: {order.customer.first_name} {order.customer.last_name}\n"
        f"Total: {order.price}€\n"
    )

    send_email(admin_email, subject, body)


def send_order_success_customer(customer_email: str, order: Order):
    subject = "Your Order Was Successful!"
    body = (
        f"Hi {order.customer.first_name} {order.customer.last_name},\n\n"
        "Thank you for your order!\n\n"
        f"Order ID: {order.id}\n"
        f"Total Paid: {order.price}€\n\n"
        "We'll notify you once your order ships."
    )

    send_email(customer_email, subject, body)
