import logging

import requests
from django.conf import settings

from win.models import ContactMessage

logger = logging.getLogger(__name__)


def send_contact_email(validated_data):
    """Send a contact form submission through Brevo's transactional API."""
    if not settings.BREVO_API_KEY:
        logger.error("Contact email is not configured: BREVO_API_KEY is missing")
        return False

    division = dict((
        ("systems", "WIN311 Systems"),
        ("services", "WIN311 Services"),
        ("general", "General enquiry"),
    )).get(validated_data.get("division"), "General enquiry")
    lines = [
        f"Name: {validated_data['name']}",
        f"Email: {validated_data['email']}",
        f"Organisation: {validated_data.get('organisation') or 'Not provided'}",
        f"Area: {division}",
    ]
    if validated_data.get("category"):
        lines.append(f"Service: {validated_data['category']}")
    lines.extend(("", "Message:", validated_data["message"]))
    payload = {
        "sender": {
            "name": settings.BREVO_SENDER_NAME,
            "email": settings.BREVO_SENDER_EMAIL,
        },
        "to": [{"email": settings.CONTACT_RECIPIENT_EMAIL}],
        "replyTo": {"email": validated_data["email"], "name": validated_data["name"]},
        "subject": f"Website enquiry from {validated_data['name']}",
        "textContent": "\n".join(lines),
    }
    try:
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={"api-key": settings.BREVO_API_KEY, "accept": "application/json"},
            json=payload,
            timeout=15,
        )
        response.raise_for_status()
        return True
    except requests.RequestException as exc:
        # Log only the provider response/status, never request headers or API key.
        status = exc.response.status_code if exc.response is not None else "unavailable"
        logger.exception("Brevo could not send contact email (HTTP %s)", status)
        return False


def store_contact_message(validated_data, ip_address=None):
    return ContactMessage.objects.create(
        name=validated_data["name"],
        email=validated_data["email"],
        organisation=validated_data.get("organisation", ""),
        division=validated_data.get("division", "general"),
        category=validated_data.get("category", ""),
        message=validated_data["message"],
        ip_address=ip_address,
    )
