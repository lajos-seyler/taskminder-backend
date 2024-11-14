import re

from django.conf import settings
from django.core.mail import send_mail


def remove_style_tags(html_content):
    # Remove everything between <style>...</style> tags
    clean_html = re.sub(r"<style.*?>.*?</style>", "", html_content, flags=re.DOTALL)
    return clean_html


def get_registration_email_html(user):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                background-color: #f9f9f9;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: auto;
                background: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            .button {{
                display: inline-block;
                background-color: #4CAF50;
                color: #fff;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Welcome to TaskMinder{f", {user.first_name}" if user.first_name else ""}!</h2>
            <p>Thank you for registering with TaskMinder! We're excited to have you onboard and help you stay organized and productive.</p>
            <p>To get started, please activate your account by clicking the button below:</p>
            <p><a href="{user.get_activation_link()}" class="button">Activate My Account</a></p>
            <p>If you have any questions or need assistance, feel free to reach out to us at <a href="mailto:support@taskminder.com">support@taskminder.com</a>.</p>
            <p>Best regards,<br>The TaskMinder Team</p>
        </div>
    </body>
    </html>
    """


def get_registration_email_plain_text(user):
    return f"""Welcome to TaskMinder{f", {user.first_name}" if user.first_name else ""}!

Thank you for registering with TaskMinder! We're excited to have you onboard and help you stay organized and productive.

To get started, please activate your account by clicking the link below:

{user.get_activation_link()}

If you have any questions or need assistance, feel free to reach out to us at support@taskminder.com.

Best regards,
The TaskMinder Team
"""


def send_registration_email(user):
    subject = "Welcome to TaskMinder - Activate Your Account!"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    html_message = get_registration_email_html(user)
    message = get_registration_email_plain_text(user)

    send_mail(
        subject,
        message=message,
        html_message=html_message,
        from_email=from_email,
        recipient_list=[to_email],
        fail_silently=False,
    )
