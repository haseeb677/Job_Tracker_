import smtplib
from email.mime.text import MIMEText

# Dummy email credentials — replace with real ones or load from env vars
EMAIL_ADDRESS = "youremail@example.com"
EMAIL_PASSWORD = "your_app_password"

def send_email(subject, body, to="youremail@example.com"):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print("✅ Email sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")