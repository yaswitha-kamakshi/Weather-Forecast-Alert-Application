"""Optional email notification. Falls back to a dry-run message if SMTP is not configured."""
import smtplib
from email.message import EmailMessage
from .config import smtp_settings


def send_email(alerts: list) -> str:
    """Return a status message. Never raises, so a mail problem can't crash the app."""
    if not alerts:
        return "No alerts to send."
    body = "\n".join(f'[{a["severity"].upper()}] {a["city"]}: {a["message"]}' for a in alerts)
    s = smtp_settings()
    if not (s["user"] and s["password"] and s["to"]):
        return "DRY-RUN: SMTP not configured (.env). Email NOT sent. Preview:\n" + body
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = s["user"], s["to"], f"Weather alerts ({len(alerts)})"
    msg.set_content(body)
    try:
        with smtplib.SMTP_SSL(s["host"], s["port"], timeout=20) as server:
            server.login(s["user"], s["password"])
            server.send_message(msg)
        return f"Email sent to {s['to']}"
    except Exception as e:
        return f"Email failed: {type(e).__name__}: {e}"
