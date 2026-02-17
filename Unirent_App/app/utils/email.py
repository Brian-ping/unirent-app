from flask_mail import Message
from app import mail

def send_reset_email(email, token):
    """
    Sends a password reset email to the user.
    """
    subject = "Password Reset - UniRent"
    reset_link = f"http://localhost:5001/new_password?token={token}"
    body = f"Click the link to reset your password: {reset_link}"

    msg = Message(subject, recipients=[email])
    msg.body = body

    try:
        mail.send(msg)
        print("Password reset email sent successfully!")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
    