# ADR-004 — Resend for Transactional Email

## Context

Users should receive a real welcome email on signup, not just an
in-app notification. We need a transactional email provider.

Options considered:

1. SendGrid (Twilio)
2. Resend
3. AWS SES
4. Mailgun

## Decision

Use Resend.

Reason:

- SendGrid rejected signup from Iran without providing a specific reason.
  Multiple attempts (with and without VPN, with a foreign virtual phone)
  were denied by their onboarding team. This is a known pattern for
  Iranian users and not a fixable problem on our side.
- Resend accepted the signup without requiring a phone number or
  credit card. The free tier covers 3,000 emails/month, which is
  sufficient for our use case.
- The Python SDK is simple (`resend.Emails.send`).
- The API key is a single string, easy to keep in env vars.
