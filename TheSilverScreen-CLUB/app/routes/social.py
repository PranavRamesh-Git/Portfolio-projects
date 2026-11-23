
from flask import Flask, Blueprint,redirect,render_template,url_for,request,jsonify,flash,session
from models import db,users,tblmovies,tbltv,screenProfiles,connectionRequest,notifications
import math
import psycopg
from psycopg.errors import UniqueViolation
from datetime import date,datetime,timedelta
from config import Config
import requests
from sqlalchemy import or_,and_
from sqlalchemy.exc import IntegrityError


social_bp = Blueprint("social",__name__)


@social_bp.route('/api/search')
def search():

    if "user_id" not in session:
        return jsonify({"error": "Please login first"}), 401

    user_id = session["user_id"]

    search = request.args.get("search",'').strip()

    if len(search) < 2:
        return jsonify({"users": []}), 200

    if len(search) > 100:
        return jsonify({"error": "Query too long"}), 400

    search_value = f"%{search}%"

    stmt = db.select(users).where(
        or_(
            users.username.ilike(search_value),
            users.fullname.ilike(search_value)
        )
    ).limit(8)

    matching_users = db.session.execute(stmt).scalars().all()

    results = []

    for user in matching_users:
        results.append({
            "user_id": user.user_id,
            "username": user.username,
            "fullname": user.fullname
        })

    return jsonify({"users": results}), 200


@social_bp.route('/api/viewProfile/<int:profile_id>')
def viewProfile(profile_id):

    if "user_id" not in session:
        return jsonify({"error": "Please login first"}), 401

    user_id = session["user_id"]

    stmt = db.select(users).where(users.user_id == profile_id)
    user = db.session.execute(stmt).scalar_one_or_none()

    if not user:
        return "User not found", 404

    stmt = db.select(connectionRequest).where(
        or_(
            and_(
                connectionRequest.requester_id == user_id,
                connectionRequest.receiver_id == profile_id
            ),
            and_(
                connectionRequest.requester_id == profile_id,
                connectionRequest.receiver_id == user_id
            )
        )
    )

    ans = db.session.execute(stmt).scalar_one_or_none()

    if profile_id == user_id:
        connection_status = "YOUR PROFILE"

    elif not ans:
        connection_status = "SEND CONNECTION REQUEST"

    elif ans.status == "ACCEPTED":
        connection_status = "CONNECTED"

    elif ans.status == "PENDING":
        if ans.requester_id == user_id:
            connection_status = "PENDING"
        else:
            connection_status = "RESPOND TO REQUEST"

    else:
        connection_status = "DECLINED"

    stmt = db.select(screenProfiles).where(
        screenProfiles.user_id == profile_id
    )

    profile = db.session.execute(stmt).scalar_one_or_none()

    if not profile:
        return "Profile not found", 404

    return render_template(
        "social_profile.html",
        connection_status=connection_status,
        user=user,
        profile=profile
    ), 200


@social_bp.route('/api/viewNotifications')
def viewNotifications():

    if "user_id" not in session:
        return jsonify({"error": "Please login first"}), 401

    user_id = session["user_id"]

    stmt = db.select(notifications).where(
        notifications.user_id == user_id
    ).order_by(notifications.sent_at.desc())

    notification_details = db.session.execute(stmt).scalars().all()

    return render_template(
        "notifications.html",
        notification_details=notification_details
    ), 200


@social_bp.route("/api/sendConnectionRequest",methods=["POST"])
def send_conn_request():

    if "user_id" not in session:
        return jsonify({"error": "Please login first"}), 401

    user_id = session["user_id"]

    data = request.get_json(silent=True) or {}
    receiver_id = data.get("receiver_id")

    if type(receiver_id) is not int:
        return jsonify({"error": "Invalid receiver ID"}), 400

    if receiver_id == user_id:
        return jsonify({"error": "Cannot send a request to yourself"}), 400

    stmt = db.select(users).where(users.user_id == user_id)
    result = db.session.execute(stmt).scalar_one_or_none()

    if not result:
        return jsonify({"error": "Requester not found"}), 404

    requester_username = result.username
    requester_fullname = result.fullname

    stmt = db.select(users).where(users.user_id == receiver_id)
    receiver = db.session.execute(stmt).scalar_one_or_none()

    if not receiver:
        return jsonify({"error": "Could not find user"}), 404

    receiver_username = receiver.username
    receiver_fullname = receiver.fullname

    stmt = db.select(connectionRequest).where(
        or_(
            and_(
                connectionRequest.requester_id == user_id,
                connectionRequest.receiver_id == receiver_id
            ),
            and_(
                connectionRequest.requester_id == receiver_id,
                connectionRequest.receiver_id == user_id
            )
        )
    )

    result = db.session.execute(stmt).scalar_one_or_none()

    if not result:

        try:
            conn = connectionRequest(
                requester_id=user_id,
                receiver_id=receiver_id
            )

            db.session.add(conn)
            db.session.flush()

            conn_id = conn.connection_id

            requester_message = f"you sent request to {receiver_username}-{receiver_fullname}"
            receiver_message = f"{requester_username}-{requester_fullname} sent you a connection request"

            requester_notif = notifications(
                user_id=user_id,
                notif_type="requester",
                connection_id=conn_id,
                message=requester_message
            )

            receiver_notif = notifications(
                user_id=receiver_id,
                notif_type="receiver",
                connection_id=conn_id,
                message=receiver_message
            )

            db.session.add(receiver_notif)
            db.session.add(requester_notif)
            db.session.commit()

            return jsonify({
                "success": "CONNECTION REQUEST SENT"
            }), 201

        except IntegrityError:
            db.session.rollback()

            return jsonify({
                "error": "Connection request already exists or could not be created"
            }), 409

    else:
        return jsonify({
            "error": "Connected or connection request already exists"
        }), 409


@social_bp.route("/api/acceptConnectionRequest", methods=["POST"])
def accept_conn_request():

    if "user_id" not in session:
        return jsonify({"error": "Please login first"}), 401

    user_id = session["user_id"]
    data = request.get_json(silent=True) or {}
    notif_id = data.get("notif_id")

    if type(notif_id) is not int:
        return jsonify({"error": "Invalid notification ID"}), 400

    stmt = db.select(notifications).where(
        notifications.notification_id == notif_id,
        notifications.user_id == user_id,
        notifications.notif_type == "receiver"
    )

    notif = db.session.execute(stmt).scalar_one_or_none()

    if not notif or not notif.connection_id:
        return jsonify({"error": "Notification not found"}), 404

    stmt = db.select(connectionRequest).where(
        connectionRequest.connection_id == notif.connection_id,
        connectionRequest.receiver_id == user_id
    ).with_for_update()

    conn = db.session.execute(stmt).scalar_one_or_none()

    if not conn:
        return jsonify({"error": "Connection request not found"}), 404

    if conn.status != "PENDING":
        return jsonify({"error": "Connection request already handled"}), 409

    stmt = (
        db.select(users)
        .where(users.user_id.in_([
            conn.requester_id,
            conn.receiver_id
        ]))
        .order_by(users.user_id)
        .with_for_update()
    )

    members = db.session.execute(stmt).scalars().all()
    members = {member.user_id: member for member in members}

    requester = members.get(conn.requester_id)
    receiver = members.get(conn.receiver_id)

    if not requester or not receiver:
        return jsonify({"error": "User not found"}), 404

    requester_connections = list(requester.connections or [])
    receiver_connections = list(receiver.connections or [])

    if receiver.user_id not in requester_connections:
        requester_connections.append(receiver.user_id)

    if requester.user_id not in receiver_connections:
        receiver_connections.append(requester.user_id)

    requester.connections = requester_connections
    receiver.connections = receiver_connections

    conn.status = "ACCEPTED"

    notif.notif_type = "ACCEPTED"
    notif.message = (
        f"You accepted the connection request from "
        f"{requester.username}"
    )

    requester_notif = notifications(
        user_id=requester.user_id,
        connection_id=conn.connection_id,
        notif_type="ACCEPTED",
        message=f"{receiver.username} accepted your connection request"
    )

    db.session.add(requester_notif)

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return jsonify({
        "success": "Connection request accepted"
    }), 200


@social_bp.route("/api/declineConnectionRequest", methods=["DELETE"])
def decline_conn_request():

    if "user_id" not in session:
        return jsonify({"error": "Please login first"}), 401

    user_id = session["user_id"]
    data = request.get_json(silent=True) or {}
    notif_id = data.get("notif_id")

    if type(notif_id) is not int:
        return jsonify({"error": "Invalid notification ID"}), 400

    stmt = db.select(notifications).where(
        notifications.notification_id == notif_id,
        notifications.user_id == user_id,
        notifications.notif_type == "receiver"
    )

    notif = db.session.execute(stmt).scalar_one_or_none()

    if not notif or not notif.connection_id:
        return jsonify({"error": "Notification not found"}), 404

    stmt = db.select(connectionRequest).where(
        connectionRequest.connection_id == notif.connection_id,
        connectionRequest.receiver_id == user_id
    ).with_for_update()

    conn = db.session.execute(stmt).scalar_one_or_none()

    if not conn:
        return jsonify({"error": "Connection request not found"}), 404

    if conn.status != "PENDING":
        return jsonify({"error": "Connection request already handled"}), 409

    requester = db.session.get(users, conn.requester_id)
    receiver = db.session.get(users, conn.receiver_id)

    if not requester or not receiver:
        return jsonify({"error": "User not found"}), 404

    conn.status = "DECLINED"

    notif.notif_type = "DECLINED"
    notif.message = (
        f"You declined the connection request from "
        f"{requester.username}"
    )

    db.session.add(notifications(
        user_id=requester.user_id,
        connection_id=conn.connection_id,
        notif_type="DECLINED",
        message=f"{receiver.username} declined your connection request"
    ))

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return jsonify({
        "success": "Connection request declined"
    }), 200
