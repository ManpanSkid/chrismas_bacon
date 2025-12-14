import logging
import os
from models import Order, PaymentMethod
import resend

logger = logging.getLogger(__name__)

# Initialize Resend with API key from environment
resend.api_key = os.getenv("RESEND_API_KEY")


# --- Refactored send_email to use Resend API ---
def send_email(to_address: str, subject: str, body: str, is_html: bool = False):
    """
    Sends an email using Resend API, supporting both plain text and HTML content.
    """
    from_email = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")

    if not resend.api_key:
        logging.error("Missing RESEND_API_KEY environment variable.")
        return

    if not from_email:
        logging.error("Missing RESEND_FROM_EMAIL environment variable.")
        return

    try:
        logging.info(f"Attempting to send email to {to_address} with subject: {subject}")

        params = {
            "from": from_email,
            "to": [to_address],
            "subject": subject,
        }

        if is_html:
            params["html"] = body
            params["text"] = "Bitte aktivieren Sie HTML, um diese E-Mail anzuzeigen."
        else:
            params["text"] = body

        response = resend.Emails.send(params)
        logging.info(f"Email successfully sent to {to_address}. Response: {response}")

    except Exception as e:
        logging.error(f"Email send failed for {to_address}: {e}")


# --- Original Admin Email (unchanged for German translation) ---
def send_new_order_received_admin(order: Order):
    """Sends a plain text notification email to the admin."""
    admin_email = os.getenv("ADMIN_EMAIL")

    if not admin_email:
        logging.error("Missing ADMIN_EMAIL environment variable.")
        return

    subject = "Neue Bestellung Eingegangen"
    body = (
        f"Eine neue Bestellung wurde aufgegeben.\n\n"
        f"Bestell-ID: {order.id}\n"
        f"Kunde: {order.customer.first_name} {order.customer.last_name}\n"
        f"Gesamtbetrag: {order.price:.2f}€\n"
    )

    send_email(admin_email, subject, body)


# --- New Professional Customer Email (German/HTML) ---
def send_order_success_customer(customer_email: str, order: Order):
    """
    Sends a professional, HTML-styled order confirmation email in German.
    """
    subject = "Ihre Bestellung war erfolgreich! | Bestell-Nr. " + order.id

    # --- Company/Contact Information Placeholders ---
    COMPANY_NAME = "Dein Weihnachtsbaum.de"
    COMPANY_LOGO_URL = "https://www.deinweihnachstbaum.de/logo.png"
    CONTACT_EMAIL = "info@deinweihnachstbaum.de"
    CONTACT_PHONE = "+49 151 2954 5560"
    PAYMENT_METHODE = "Barzahlung vor Ort"

    if order.payment_method == PaymentMethod.Stripe:
        PAYMENT_METHODE = "Kartenzahlung"

    # --- German Translation and Detail Formatting ---
    tree_stand_status = "Ja" if order.tree_stand else "Nein"

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
                <p>Sehr geehrte/r Frau/Herr <strong>{order.customer.last_name}</strong>,</p>
                <p>Vielen Dank für Ihre Bestellung bei <strong>{COMPANY_NAME}</strong>! Ihre Bestellung wurde erfolgreich platziert und wird in Kürze bearbeitet.</p>

                <h2>Zusammenfassung Ihrer Bestellung</h2>
                <p><strong>Bestell-ID:</strong> <span class="highlight">{order.id}</span></p>
                <p><strong>Bestelldatum:</strong> {order.order_date.strftime("%d.%m.%Y, %H:%M")} Uhr</p>

                <h3>Details</h3>
                <table class="details-table">
                    <tr>
                        <th colspan="2" style="background-color: #e6ffe6;">Ihr Weihnachtsbaum</th>
                    </tr>
                    <tr>
                        <td><strong>Baumart:</strong></td>
                        <td>{order.tree.name}</td>
                    </tr>
                    <tr>
                        <td><strong>Größe:</strong></td>
                        <td>{order.size.name}</td>
                    </tr>
                    <tr>
                        <td><strong>Lieferumfang:</strong></td>
                        <td>{order.package.name}</td>
                    </tr>
                    <tr>
                        <td><strong>Christbaumständer:</strong></td>
                        <td>{tree_stand_status}</td>
                    </tr>
                    <tr>
                        <th colspan="2" style="background-color: #e6ffe6;">Liefer- & Zahlungsdetails</th>
                    </tr>
                    <tr>
                        <td><strong>Lieferadresse:</strong></td>
                        <td>{order.customer.address}, {order.customer.postal_code} {order.customer.city}</td>
                    </tr>
                    <tr>
                        <td><strong>Zahlungsmethode:</strong></td>
                        <td>{PAYMENT_METHODE}</td>
                    </tr>
                </table>

                <p style="text-align: right; font-size: 1.2em;">
                    <strong>Gesamtbetrag (inkl. MwSt.):</strong> <span class="highlight">{order.price:.2f}€</span>
                </p>

                <p>Wir werden Sie benachrichtigen, sobald Ihre Bestellung versandbereit ist und die Lieferung erfolgt.</p>
                <p>Bei Fragen zu Ihrer Bestellung, antworten Sie einfach auf diese E-Mail oder kontaktieren Sie uns unter den unten angegebenen Kontaktdaten.</p>

                <p>Mit freundlichen Grüßen,</p>
                <p>Ihr Team von <strong>{COMPANY_NAME}</strong></p>
            </div>

            <div class="footer">
                <p><strong>Kontakt:</strong></p>
                <p>E-Mail: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
                <p>Telefon: {CONTACT_PHONE}</p>
            </div>
        </div>
    </body>
    </html>
    """

    send_email(customer_email, subject, html_body, is_html=True)