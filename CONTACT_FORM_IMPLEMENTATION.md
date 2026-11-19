# WIN311 contact form

The contact page accepts a standard Django form POST. Valid submissions are
saved as `ContactMessage` records in the configured PostgreSQL database before
Django sends an inbox notification and a submitter acknowledgement through
Brevo's SMTP relay using Django's email backend. Both messages contain plain-text and HTML
alternatives. The inbox notification uses the submitter's address as `Reply-To`.

When the SMTP backend accepts both emails, the contact view
redirects to a server-rendered confirmation state. If delivery fails, the
saved enquiry remains available in the database and the form displays an error
instead of a success state. Tests use Django's in-memory email backend and do not contact a live
provider.

The client acknowledgement is first in the batch, followed by the inbox
notification. Django opens one SMTP connection for that batch and closes it
after sending; it is not kept open continuously. SMTP acceptance does not
prove that an email reached the recipient's inbox. If a message is missing,
check spam/junk folders and Brevo's delivery logs, and verify the sender
domain's email authentication records.

## Environment configuration

Configure these values in the deployment environment (Render's environment
settings are declared in `render.yaml`):

- `BREVO_SMTP_HOST` (defaults to `smtp-relay.brevo.com`)
- `BREVO_SMTP_PORT` (defaults to `2525`; Render Free blocks outbound SMTP on port `587`)
- `BREVO_SMTP_LOGIN`
- `BREVO_SMTP_KEY` (Brevo SMTP key, not the API key)
- `BREVO_SMTP_USE_TLS`
- `BREVO_SMTP_USE_SSL`

For local development, set the same values in the ignored local environment
file or process environment. The sender and recipient addresses default to
`win311tech@gmail.com` in Django settings, so they do not need Render
environment variables. You can optionally override them with
`DEFAULT_FROM_EMAIL` or `CONTACT_RECIPIENT_EMAIL`; the sender must be verified
in Brevo. Google Console OAuth settings are not used by this SMTP configuration.
Never commit SMTP credentials. Keep the existing `DATABASE_URL`
PostgreSQL configuration in place.

## Checks

Run the contact tests and Django system check with:

```powershell
python manage.py test win.tests
python manage.py check
```
