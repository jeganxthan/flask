from flask import Blueprint, request, jsonify

from config.otp_utility import generate_otp
from models.auth import User
from db import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.otp import OTP
import datetime
import random
from config.email_service import send_otp_email

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not password or not email:
        return jsonify({"error": "All fields are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    # Create new user
    new_user = User(username=username, email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    # 🔹 Generate OTP
    otp_code = generate_otp(new_user.id)

    # 🔹 Send OTP via Gmail
    send_otp_email(new_user.email, otp_code)

    return jsonify({
        "message": "User registered successfully. OTP has been sent to your email."
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not password or not email:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({"access_token": access_token}), 200

    return jsonify({"error": "Invalid credentials"}), 401


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }), 200

@auth_bp.route('/request-otp', methods=['POST'])
def request_otp():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Generate OTP
    otp_code = generate_otp(user.id)

    # TODO: send otp_code via email (Flask-Mail) or SMS (Twilio)
    print(f"DEBUG: OTP for {email} = {otp_code}")  # for testing only

    return jsonify({"message": "OTP sent successfully"}), 200


@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get("email")
    code = data.get("otp")

    if not email or not code:
        return jsonify({"error": "Email and OTP are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    otp = OTP.query.filter_by(user_id=user.id, code=code).first()
    if not otp:
        return jsonify({"error": "Invalid OTP"}), 400

    if otp.expires_at < datetime.datetime.utcnow():
        db.session.delete(otp)
        db.session.commit()
        return jsonify({"error": "OTP expired"}), 400

    # ✅ OTP valid → delete it so it can't be reused
    db.session.delete(otp)
    db.session.commit()

    # ✅ Issue JWT token
    access_token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": access_token}), 200
