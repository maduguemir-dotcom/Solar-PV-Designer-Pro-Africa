# Stage 6I — Production Email Integration

Adds reusable notification templates, an SMTP provider adapter, and a settings page documenting deployment-secret configuration.

The SMTP adapter is opt-in and does not send mail unless instantiated and invoked with valid runtime credentials. Sandbox delivery remains available for testing.

Recommended environment variables:
- EMAIL_PROVIDER
- EMAIL_SMTP_HOST
- EMAIL_SMTP_PORT
- EMAIL_SMTP_USERNAME
- EMAIL_SMTP_PASSWORD
- EMAIL_SENDER
- EMAIL_SMTP_USE_TLS

Never commit credentials to the repository.
