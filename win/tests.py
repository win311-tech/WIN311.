from smtplib import SMTPServerDisconnected
from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ContactMessage


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    EMAIL_HOST="smtp-relay.brevo.com",
    EMAIL_PORT=587,
    EMAIL_HOST_USER="test-smtp-login",
    EMAIL_HOST_PASSWORD="test-smtp-key",
    EMAIL_USE_TLS=True,
    EMAIL_USE_SSL=False,
    EMAIL_TIMEOUT=10,
    DEFAULT_FROM_EMAIL="contact@example.com",
    CONTACT_RECIPIENT_EMAIL="inbox@example.com",
)
class ContactViewTests(TestCase):
    def setUp(self):
        self.url = reverse("contact")
        self.valid_data = {
            "name": "Ama Mensah",
            "email": "ama@example.com",
            "organisation": "Acme Studio",
            "division": "services",
            "category": "Web Development",
            "message": "I would like to discuss a new website.",
        }

    def test_get_displays_the_contact_form(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'method="post"')
        self.assertContains(response, "Send your enquiry")
        self.assertNotContains(response, "Enquiry sent")

    @patch("win.services.contact_service.get_connection")
    def test_invalid_post_renders_validation_errors_without_saving_or_sending(
        self, get_connection
    ):
        response = self.client.post(
            self.url,
            {
                **self.valid_data,
                "email": "not-an-email",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a valid email address")
        self.assertContains(response, 'id="contactForm"')
        self.assertEqual(ContactMessage.objects.count(), 0)
        get_connection.assert_not_called()

    @override_settings(EMAIL_HOST_USER="", EMAIL_HOST_PASSWORD="")
    @patch("win.services.contact_service.get_connection")
    def test_missing_brevo_smtp_credentials_are_reported_without_connecting(
        self, get_connection
    ):
        with self.assertLogs("win.services.contact_service", level="ERROR") as logs:
            response = self.client.post(self.url, self.valid_data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your enquiry was saved")
        self.assertIn(
            "missing: BREVO_SMTP_LOGIN, BREVO_SMTP_KEY.",
            "\n".join(logs.output),
        )
        get_connection.assert_not_called()

    def test_valid_post_saves_and_sends_two_multipart_emails(self):
        data = {
            **self.valid_data,
            "message": 'Please review <script>alert("x")</script>.',
        }
        response = self.client.post(self.url, data)

        self.assertRedirects(response, self.url, fetch_redirect_response=False)
        message = ContactMessage.objects.get()
        self.assertEqual(message.name, data["name"])
        self.assertEqual(message.email, data["email"])
        self.assertEqual(message.division, data["division"])
        self.assertEqual(message.category, data["category"])
        self.assertEqual(len(mail.outbox), 2)

        acknowledgement, notification = mail.outbox
        self.assertEqual(acknowledgement.to, ["ama@example.com"])
        self.assertEqual(notification.to, ["inbox@example.com"])
        self.assertEqual(notification.reply_to, ["ama@example.com"])
        self.assertIn("received and reserved", acknowledgement.body)
        self.assertIn("received and reserved", acknowledgement.alternatives[0][0])
        for email_message in (notification, acknowledgement):
            self.assertEqual(email_message.from_email, "contact@example.com")
            self.assertEqual(len(email_message.alternatives), 1)
            self.assertEqual(email_message.alternatives[0][1], "text/html")
            self.assertIn("Please review", email_message.body)
            self.assertIn("&lt;script&gt;", email_message.alternatives[0][0])
            self.assertNotIn("<script>", email_message.alternatives[0][0])
            self.assertRegex(
                email_message.alternatives[0][0],
                r'src="http://testserver/static/images/favicon-email(?:\.[0-9a-f]+)?\.png"',
            )
            self.assertIn('alt="WIN311 company logo"', email_message.alternatives[0][0])
            self.assertIn("border-left:2px solid #777d75", email_message.alternatives[0][0])
            self.assertIn("letter-spacing:1px;\">WIN311</p>", email_message.alternatives[0][0])
            self.assertIn("letter-spacing:1.5px;\">CONTACT</p>", email_message.alternatives[0][0])
            self.assertIn("background:#ffffff", email_message.alternatives[0][0])
            self.assertIn("color:#000000", email_message.alternatives[0][0])
            self.assertIn("padding:16px", email_message.alternatives[0][0])
            self.assertIn("padding:20px", email_message.alternatives[0][0])
            self.assertIn(
                "word-break:break-all;overflow-wrap:anywhere",
                email_message.alternatives[0][0],
            )
            self.assertIn(
                "font-family:Arial,Helvetica,sans-serif",
                email_message.alternatives[0][0],
            )
            self.assertNotIn("Manrope", email_message.alternatives[0][0])
        self.assertIn(
            "style=\"padding:8px 0;word-break:break-all;overflow-wrap:anywhere;\">"
            "ama@example.com</td>",
            notification.alternatives[0][0],
        )

        response = self.client.get(response.url)
        self.assertContains(response, "<h2 id=\"success-heading\">Enquiry sent</h2>", html=True)
        self.assertContains(response, 'class="success-art"')
        self.assertContains(response, "Our team will reply as soon as we can.")
        self.assertNotContains(response, 'id="contactForm"')

    @patch("win.services.contact_service.get_connection")
    def test_smtp_failure_keeps_the_form_and_shows_an_error(self, get_connection):
        get_connection.return_value.send_messages.side_effect = SMTPServerDisconnected(
            "provider disconnected"
        )

        with self.assertLogs("win.services.contact_service", level="ERROR") as logs:
            response = self.client.post(self.url, self.valid_data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your enquiry was saved")
        self.assertContains(response, "Please try again later or email us directly.")
        self.assertContains(response, 'id="contactForm"')
        self.assertNotContains(response, "Enquiry sent")
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertIn(
            "Contact email delivery failed (SMTPServerDisconnected).",
            "\n".join(logs.output),
        )

    @patch("win.services.contact_service.get_connection")
    def test_partial_smtp_delivery_sends_both_emails_in_one_connection(
        self, get_connection
    ):
        get_connection.return_value.send_messages.return_value = 1

        with self.assertLogs("win.services.contact_service", level="ERROR") as logs:
            response = self.client.post(self.url, self.valid_data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your enquiry was saved")
        self.assertEqual(get_connection.return_value.send_messages.call_count, 1)
        messages = get_connection.return_value.send_messages.call_args.args[0]
        self.assertEqual([message.to for message in messages], [
            ["ama@example.com"],
            ["inbox@example.com"],
        ])
        self.assertIn(
            "Brevo SMTP accepted 1 of 2 contact emails.",
            "\n".join(logs.output),
        )
