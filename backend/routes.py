from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from models import db, User, Seat, Booking
from app import socketio   # ✅ import socketio from app.py
from auth import create_user, verify_user

bp = Blueprint("routes", __name__)

# -------------------------
# User Registration
# -------------------------
@bp.route("/register", methods=["POST"])
def register():
    data = request.json
    if User.query.filter_by(erp=data["erp"]).first():
        return jsonify({"msg": "User exists"}), 400
    user = create_user(data["erp"], data["name"], data.get("email"), data["password"])
    return jsonify({"msg": "created", "id": user.id})

# -------------------------
# Login
# -------------------------
@bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = verify_user(data["erp"], data["password"])
    if not user:
        return jsonify({"msg": "bad credentials"}), 401
    token = create_access_token(identity=str(user.id))  # ✅ store as string
    return jsonify({"access_token": token, "user": {"id": user.id, "erp": user.erp}})

# -------------------------
# Seat Availability
# -------------------------
@bp.route("/availability", methods=["GET"])
@jwt_required()
def availability():
    seats = Seat.query.all()
    return jsonify([{
        "id": s.id,
        "label": s.label,
        "status": s.status,
        "user_id": s.current_user_id
    } for s in seats])

# -------------------------
# Hold a seat
# -------------------------
@bp.route("/hold", methods=["POST"])
@jwt_required()
def hold():
    user_id = int(get_jwt_identity())   # ✅ cast back to int
    seat_id = request.json["seat_id"]
    hold_seconds = 120

    seat = Seat.query.get(seat_id)
    if seat.status != "free":
        return jsonify({"msg": "Seat not free"}), 409

    expires_at = datetime.utcnow() + timedelta(seconds=hold_seconds)
    booking = Booking(seat_id=seat.id, user_id=user_id, status="reserved", expires_at=expires_at)

    db.session.add(booking)
    seat.status = "reserved"
    seat.current_user_id = user_id
    db.session.commit()

    # ✅ Realtime seat update
    socketio.emit("seat_update", {"seat_id": seat.id, "status": "reserved", "user_id": user_id})

    return jsonify({"msg": "held", "booking_id": booking.id, "expires_at": expires_at.isoformat()})

# -------------------------
# Confirm booking
# -------------------------
@bp.route("/confirm", methods=["POST"])
@jwt_required()
def confirm():
    user_id = int(get_jwt_identity())   # ✅ cast back to int
    booking_id = request.json["booking_id"]

    booking = Booking.query.get(booking_id)
    if not booking or booking.user_id != user_id or booking.status != "reserved":
        return jsonify({"msg": "Invalid booking"}), 400

    booking.status = "active"
    booking.start_time = datetime.utcnow()
    booking.expires_at = None

    seat = Seat.query.get(booking.seat_id)
    seat.status = "occupied"

    db.session.commit()

    # ✅ Realtime seat update
    socketio.emit("seat_update", {"seat_id": seat.id, "status": "occupied", "user_id": user_id})

    return jsonify({"msg": "confirmed"})

# -------------------------
# Release booking
# -------------------------
@bp.route("/release", methods=["POST"])
@jwt_required()
def release():
    user_id = int(get_jwt_identity())   # ✅ cast back to int
    seat_id = request.json["seat_id"]

    seat = Seat.query.get(seat_id)
    if not seat or seat.current_user_id != user_id:
        return jsonify({"msg": "Not your seat"}), 403

    booking = Booking.query.filter_by(seat_id=seat.id, user_id=user_id, status="active").first()
    if booking:
        booking.status = "ended"
        booking.end_time = datetime.utcnow()

    seat.status = "free"
    seat.current_user_id = None

    db.session.commit()

    # ✅ Realtime seat update
    socketio.emit("seat_update", {"seat_id": seat.id, "status": "free", "user_id": None})

    return jsonify({"msg": "released"})

# -------------------------
# Reset (for testing)
# -------------------------
@bp.route("/reset", methods=["POST"])
def reset():
    for seat in Seat.query.all():
        seat.status = "free"
        seat.current_user_id = None
    Booking.query.delete()
    db.session.commit()

    # ✅ Notify all clients
    socketio.emit("reset_done", {"msg": "reset done"})

    return jsonify({"msg": "reset done"})
