from dataclasses import dataclass
import logging
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.templatetags.static import static
from django.template.loader import render_to_string

from win.models import ContactMessage

logger = logging.getLogger(__name__)

DIVISION_LABELS = {
    "general": "General enquiry",
    "systems": "WIN311 Systems",
    "services": "WIN311 Services",
}


@dataclass(frozen=True)
class ContactSubmissionResult:
    delivered: bool
    error_code: str = ""


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


def send_contact_emails(contact_message, request=None):
    required_settings = {
        "BREVO_SMTP_HOST": settings.EMAIL_HOST,
        "BREVO_SMTP_LOGIN": settings.EMAIL_HOST_USER,
        "BREVO_SMTP_KEY": settings.EMAIL_HOST_PASSWORD,
        "DEFAULT_FROM_EMAIL": settings.DEFAULT_FROM_EMAIL,
        "CONTACT_RECIPIENT_EMAIL": settings.CONTACT_RECIPIENT_EMAIL,
    }
    missing_settings = [
        name for name, value in required_settings.items() if not value
    ]
    if missing_settings:
        logger.error(
            "Contact email delivery is not configured; missing: %s.",
            ", ".join(missing_settings),
        )
        return ContactSubmissionResult(False, "not_configured")

    try:
        favicon_path = static("images/favicon-email.png")
    except ValueError:
        favicon_path = (
            f"{settings.STATIC_URL.rstrip('/')}/images/favicon-email.png"
        )
    context = {
        "submission": contact_message,
        "division_label": DIVISION_LABELS.get(
            contact_message.division, contact_message.division
        ),
        "favicon_url": (
            request.build_absolute_uri(favicon_path) if request else favicon_path
        ),
    }
    notification_text = render_to_string(
        "emails/contact_notification.txt", context
    )
    notification_html = render_to_string(
        "emails/contact_notification.html", context
    )
    acknowledgement_text = render_to_string(
        "emails/contact_acknowledgement.txt", context
    )
    acknowledgement_html = render_to_string(
        "emails/contact_acknowledgement.html", context
    )

    acknowledgement = EmailMultiAlternatives(
        subject="We received your enquiry — WIN311",
        body=acknowledgement_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[contact_message.email],
    )
    acknowledgement.attach_alternative(acknowledgement_html, "text/html")

    notification = EmailMultiAlternatives(
        subject="New enquiry from the WIN311 contact form",
        body=notification_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.CONTACT_RECIPIENT_EMAIL],
        reply_to=[contact_message.email],
    )
    notification.attach_alternative(notification_html, "text/html")

    connection = get_connection(fail_silently=False)
    try:
        sent_count = connection.send_messages([acknowledgement, notification])
    except (OSError, SMTPException) as exc:
        logger.error("Contact email delivery failed (%s).", type(exc).__name__)
        return ContactSubmissionResult(False, "delivery_failed")

    if sent_count != 2:
        logger.error("Brevo SMTP accepted %s of 2 contact emails.", sent_count)
        return ContactSubmissionResult(False, "delivery_incomplete")

    logger.info("Brevo SMTP accepted the acknowledgement and notification.")
    return ContactSubmissionResult(True)


def submit_contact_message(validated_data, ip_address=None, request=None):
    contact_message = store_contact_message(validated_data, ip_address)
    return send_contact_emails(contact_message, request=request)
