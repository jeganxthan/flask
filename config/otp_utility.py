import random, datetime
from models.otp import OTP
from db import db

def generate_otp(user_id):
    code = str(random.randint(100000, 999999))  # 6-digit OTP
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)

    otp = OTP(user_id=user_id, code=code, expires_at=expires_at)
    db.session.add(otp)
    db.session.commit()

    return code
