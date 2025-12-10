import logging
import os
import smtplib
from email.message import EmailMessage
from models import Order


# --- Refactored send_email to support HTML content ---
def send_email(to_address: str, subject: str, body: str, is_html: bool = False):
    """
    Sends an email, supporting both plain text and HTML content.
    """
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", 587))
    # Note: I used SMTP_USER/SMTP_INFO as the sender/login
    user = os.getenv("SMTP_INFO")
    password = os.getenv("SMTP_INFO_PW")

    if not all([host, user, password]):
        logging.error("Missing one or more SMTP environment variables (HOST, USER, PW).")
        return

    try:
        msg = EmailMessage()
        msg["From"] = user
        msg["To"] = to_address
        msg["Subject"] = subject

        if is_html:
            msg.set_content("Bitte aktivieren Sie HTML, um diese E-Mail anzuzeigen.", subtype="plain")
            msg.add_alternative(body, subtype="html")
        else:
            msg.set_content(body)

        logging.info(f"Attempting to send email to {to_address} with subject: {subject}")

        with smtplib.SMTP(host, port) as smtp:
            # Standard TLS setup for many providers
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(user, password)
            smtp.send_message(msg)

        logging.info(f"Email successfully sent to {to_address}.")

    except Exception as e:
        logging.error(f"Email send failed for {to_address}: {e}")


# --- Original Admin Email (unchanged for German translation) ---
def send_new_order_received_admin(order: Order):
    """Sends a plain text notification email to the admin."""
    # Assuming SMTP_USER is the admin's email for simplicity,
    # or you might want a separate ADMIN_EMAIL env var.
    admin_email = os.getenv("SMTP_USER")

    subject = "Neue Bestellung Eingegangen"  # Translated for better internal consistency
    body = (
        f"Eine neue Bestellung wurde aufgegeben.\n\n"
        f"Bestell-ID: {order.id}\n"
        f"Kunde: {order.customer.first_name} {order.customer.last_name}\n"
        f"Gesamtbetrag: {order.price:.2f}€\n"  # Formatted for two decimal places
    )

    send_email(admin_email, subject, body)


# --- New Professional Customer Email (German/HTML) ---
def send_order_success_customer(customer_email: str, order: Order):
    """
    Sends a professional, HTML-styled order confirmation email in German.
    """
    subject = "Ihre Bestellung war erfolgreich! | Bestell-Nr. " + order.id

    # --- Company/Contact Information Placeholders ---
    # In a real app, these would come from env vars or a config file
    COMPANY_NAME = "Dein Weihnachtsbaum"
    COMPANY_LOGO_URL = "https://www.deinweihnachstbaum.de/logo.png"  # Placeholder
    CONTACT_EMAIL = "info@deinweihnachstbaum.de"
    CONTACT_PHONE = "+49 151 2954 5560"

    # --- German Translation and Detail Formatting ---
    tree_stand_status = "Ja" if order.tree_stand else "Nein"
    delivery_date_str = order.delivery.delivery_date.strftime("%d.%m.%Y")

    # Generate the HTML email body
    html_body = f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{subject}</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ width: 100%; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; }}
            .header {{ background-color: #006400; color: #ffffff; padding: 10px 20px; text-align: center; }}
            .header img {{ max-width: 150px; height: auto; }}
            .content {{ padding: 20px 0; }}
            .details-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            .details-table th, .details-table td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            .details-table th {{ background-color: #f2f2f2; }}
            .footer {{ margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; text-align: center; font-size: 0.9em; color: #777; }}
            .highlight {{ color: #006400; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="{COMPANY_LOGO_URL}" alt="{COMPANY_NAME} Logo" style="display: block; margin: 0 auto;">
                <h1 style="margin: 5px 0 0 0; font-size: 24px;">Bestellbestätigung</h1>
            </div>

            <div class="content">
                <p>Sehr geehrte/r Frau/Herr **{order.customer.last_name}**,</p>
                <p>Vielen Dank für Ihre Bestellung bei **{COMPANY_NAME}**! Ihre Bestellung wurde erfolgreich platziert und wird in Kürze bearbeitet.</p>

                <h2>Zusammenfassung Ihrer Bestellung</h2>
                <p><strong>Bestell-ID:</strong> <span class="highlight">{order.id}</span></p>
                <p><strong>Bestelldatum:</strong> {order.order_date.strftime("%d.%m.%Y, %H:%M")} Uhr</p>

                <h3>Details</h3>
                <table class="details-table">
                    <tr>
                        <th colspan="2" style="background-color: #e6ffe6;">Ihr Weihnachtsbaum</th>
                    </tr>
                    <tr>
                        <td>**Baumart:**</td>
                        <td>{order.tree.name}</td>
                    </tr>
                    <tr>
                        <td>**Größe:**</td>
                        <td>{order.size.height_cm} cm</td>
                    </tr>
                    <tr>
                        <td>**Verpackung:**</td>
                        <td>{order.package.type}</td>
                    </tr>
                    <tr>
                        <td>**Christbaumständer:**</td>
                        <td>{tree_stand_status}</td>
                    </tr>
                    <tr>
                        <th colspan="2" style="background-color: #e6ffe6;">Liefer- & Zahlungsdetails</th>
                    </tr>
                    <tr>
                        <td>**Lieferdatum:**</td>
                        <td>{delivery_date_str}</td>
                    </tr>
                    <tr>
                        <td>**Lieferadresse:**</td>
                        <td>{order.delivery.street}, {order.delivery.zip_code} {order.delivery.city}</td>
                    </tr>
                    <tr>
                        <td>**Zahlungsmethode:**</td>
                        <td>{order.payment_method.name}</td>
                    </tr>
                </table>

                <p style="text-align: right; font-size: 1.2em;">
                    **Gesamtbetrag (inkl. MwSt.):** <span class="highlight">{order.price:.2f}€</span>
                </p>

                <p>Wir werden Sie benachrichtigen, sobald Ihre Bestellung versandbereit ist und die Lieferung erfolgt.</p>
                <p>Bei Fragen zu Ihrer Bestellung, antworten Sie einfach auf diese E-Mail oder kontaktieren Sie uns unter den unten angegebenen Kontaktdaten.</p>

                <p>Mit freundlichen Grüßen,</p>
                <p>Ihr Team von **{COMPANY_NAME}**</p>
            </div>

            <div class="footer">
                <p>**Kontakt:**</p>
                <p>E-Mail: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
                <p>Telefon: {CONTACT_PHONE}</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Pass is_html=True to send_email
    send_email(customer_email, subject, html_body, is_html=True)