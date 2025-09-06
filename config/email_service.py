from flask_mail import Message
from extensions import mail
from flask import render_template

def send_otp_email(to_email, otp_code):
    msg = Message(
        subject="Verify Your Email",
        recipients=[to_email],
        sender=("Flask App", "your_email@gmail.com"),
        html=render_template("otp_email.html", otp=otp_code)
    )
    mail.send(msg)
