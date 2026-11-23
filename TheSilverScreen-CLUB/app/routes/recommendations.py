
from flask import Flask, Blueprint,redirect,render_template,url_for,request,jsonify,flash,session
from models import db,users,tblmovies,tbltv,screenProfiles,connectionRequest,notifications,recommendations,vw_recommendations
import math
import psycopg
from psycopg.errors import UniqueViolation
from datetime import date,datetime,timedelta
from config import Config
import requests
from sqlalchemy import or_,and_
from sqlalchemy.exc import IntegrityError
from app.extensions import limiter,user_or_ip


recommendations_bp = Blueprint("recommendations",__name__)

@recommendations_bp.route("/api/recommendationForm", methods=["POST"])
def showRecommendationForm():

    if "user_id" not in session:
        return jsonify({"error": "Please login first"}), 401

    user_id = session["user_id"]
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    tmdb_id = data.get("tmdb_id")

    if type(tmdb_id) is not int or tmdb_id <= 0:
        return jsonify({"error": "Invalid TMDB ID"}), 400

    media_type = data.get("media_type")

    if media_type not in ("movie", "tv"):
        return jsonify({"error": "Invalid media type"}), 400

    media_type = data.get("media_type")
    title = data.get("title")
    overview = data.get("overview")
    popularity = data.get("popularity")
    release_date = data.get("release_date")
    poster_path = data.get("poster_path")
    vote_average = data.get("vote_average")
    vote_count= data.get("vote_count")

    if media_type not in ("movie", "tv"):
        return jsonify({
            "error": "Invalid media type"
        }), 400

    if type(tmdb_id) is not int or int(tmdb_id) <= 0:
        return jsonify({
            "error": "Invalid TMDB ID"
        }), 400

    if not isinstance(title, str) or not title.strip() or len(title) > 200:
        return jsonify({
            "error": "Invalid title"
        }), 400

    #  Convert release_date string into Python date
    try:
        if release_date and release_date != "TBA":
            release_date = date.fromisoformat(release_date)
        else:
            release_date = None

    except (ValueError, TypeError):
        return jsonify({
            "error": "Invalid release date"
        }), 400


    stmt = db.select(users).where(users.user_id == user_id)
    user_info = db.session.execute(stmt).scalar_one_or_none()

    if not user_info:
        return jsonify({"error": "User not found"}), 404

    connections = list(user_info.connections or [])

    result = []

    for id in connections:

        stmt = db.select(users).where(users.user_id == id)
        user = db.session.execute(stmt).scalar_one_or_none()

        if user:
            connection = {
                "user_id": id,
                "username": user.username,
                "fullname": user.fullname
            }

            result.append(connection)

    return render_template(
        "recommend_form.html",
        result=result,
        tmdb_id=int(tmdb_id),
        media_type=media_type,
        title = title,
        overview = overview,
        popularity = popularity,
        release_date = release_date,
        poster_path = poster_path,
        vote_average = vote_average,
        vote_count= vote_count        
    ), 200



@recommendations_bp.route("/api/sendRecommendation", methods=["POST"])
@limiter.limit("20 per hour", key_func=user_or_ip)
def sendRecommendation():

    if "user_id" not in session:
        return jsonify({"error": "Please login first"}), 401

    user_id = session["user_id"]

    tmdb_id = request.form.get("tmdb_id", type=int)

    if tmdb_id is None or tmdb_id <= 0:
        return jsonify({"error": "Invalid TMDB ID"}), 400
    
    media_type = request.form.get("media_type")
    selected_ids = request.form.getlist("recommend_to")

    title = request.form.get("title")
    overview = request.form.get("overview")
    poster_path = request.form.get("poster_path")

    popularity = request.form.get("popularity", type=float)
    vote_average = request.form.get("vote_average", type=float)
    vote_count = request.form.get("vote_count", type=int)

    release_date = request.form.get("release_date")


    if media_type not in ("movie", "tv"):
        return jsonify({"error": "Invalid media type"}), 400

    if not isinstance(title, str) or not title.strip() or len(title) > 200:
        return jsonify({"error": "Invalid title"}), 400

    try:
        if release_date and release_date != "TBA":
            release_date = date.fromisoformat(release_date)
        else:
            release_date = None
    except ValueError:
        return jsonify({"error": "Invalid release date"}), 400
    


    user_info = db.session.get(users, user_id)

    if not user_info:
        return jsonify({"error": "User not found"}), 404

    connections = list(user_info.connections or [])

    if "ALL CONNECTIONS" in selected_ids:
        receiver_ids = connections

    else:
        try:
            receiver_ids = [int(id) for id in selected_ids]
        except ValueError:
            return jsonify({"error": "Invalid connection ID"}), 400

    receiver_ids = list(set(receiver_ids))

    if not receiver_ids:
        return jsonify({"error": "Select at least one connection"}), 400

    if not set(receiver_ids).issubset(set(connections)):
        return jsonify({"error": "Invalid connections selected"}), 403

    try:
        for receiver_id in receiver_ids:

            rec = recommendations(
                sender_id=user_id,
                receiver_id=receiver_id,
                media_type=media_type,
                recommendation_id=int(tmdb_id),
                title=title,
                poster_path=poster_path,
                release_date=release_date,
                overview=overview,
                popularity=popularity,
                vote_average=vote_average,
                vote_count=vote_count                
            )

            db.session.add(rec)

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    flash("recommendation sent!", "success")
    return redirect(url_for("main.home"))


@recommendations_bp.route("/api/getRecommendation")
def getRecommendation():

    if "user_id" not in session:
        return jsonify({"error": "Please login first"}), 401

    user_id = session["user_id"]

    stmt = db.select(vw_recommendations).where(vw_recommendations.sender_id == user_id).order_by(vw_recommendations.created_at.desc())
    result_sent = db.session.execute(stmt).scalars().all()

    stmt = db.select(vw_recommendations).where(vw_recommendations.receiver_id == user_id).order_by(vw_recommendations.created_at.desc())
    result_get = db.session.execute(stmt).scalars().all()
    sent = []
    get = []
    if not result_sent:
        sent = []
    else:
        for item in result_sent:
            sent.append({
                "tmdb_id": item.recommendation_id,
                "title": item.title,
                "poster_path": item.poster_path,
                "release_date": (item.release_date.isoformat() if item.release_date else None),
                "overview": item.overview,
                "popularity": item.popularity,
                "vote_average": item.vote_average,
                "vote_count": item.vote_count,
                "media_type": item.media_type,
                "sender_username": item.sender_username,
                "receiver_username": item.receiver_username
            })

    if not result_get:
        get = []
    else:
        for item in result_get:
            get.append({
                "tmdb_id": item.recommendation_id,
                "title": item.title,
                "poster_path": item.poster_path,
                "release_date": (item.release_date.isoformat() if item.release_date else None),
                "overview": item.overview,
                "popularity": item.popularity,
                "vote_average": item.vote_average,
                "vote_count": item.vote_count,
                "media_type": item.media_type,
                "sender_username": item.sender_username,
                "receiver_username": item.receiver_username                
            })

    stmt = db.select(tblmovies).where(tblmovies.user_id == user_id)
    libraryMovies = db.session.execute(stmt).scalars().all()
    mymovies = []

    for movie in libraryMovies:
        mymovies.append({
            "tmdb_id": movie.tmdb_id,
        })

    
    stmt = db.select(tbltv.tmdb_id).where(
        tbltv.user_id == user_id
    )

    library_tv_tmdb_ids = db.session.execute(stmt).scalars().all()

    mytvs = []

    for tmdb_id in library_tv_tmdb_ids:
        mytvs.append({
            "tmdb_id": tmdb_id
        })

    return jsonify({
        "sent": sent,
        "get" : get,
        "mymovies": mymovies,
        "mytvs": mytvs
    })
        
