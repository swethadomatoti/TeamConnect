from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

from django.core.mail import send_mail
from django.conf import settings
import os

def send_welcome_celeryemail(username, user_email):
    subject = "Welcome!"
    message = f"Hi {username}, welcome to TeamConnect!"

    # Check if running on Render (no email sending allowed)
    if os.environ.get('RENDER'):
        print(f"Skipping email send to {user_email} (Render does not allow SMTP in free plan).")
        return

    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email], fail_silently=False)
        print(f"Email sent successfully to {user_email}")
    except Exception as e:
        print(f"Email sending failed: {e}")

 

# @shared_task # Marks the function as a Celery task
# def send_welcome_celeryemail(username,user_email):
#     subject = "Welcome to Django App!"
#     message = f"Hi {username},\n\nThank you for registering. You can now log in using your credentials."
#     send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email], fail_silently=False)
#     print(f"Welcome email sent to {user_email}") # debug output
#     return "Email Sent Successfully" # Return a success message
# @shared_task
def send_otp_email(user, otp):
    subject = 'Your Password Reset OTP'
    message = f"""Hi {user.username},
                    Your OTP for password reset is: {otp}
                    It will expire in 1 minutes.
                    If you did not request this, ignore this email.
               """
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
    print(f"OTP email sent to {user.email}") # debug output
    return "OTP Email Sent Successfully" # Return a success message
