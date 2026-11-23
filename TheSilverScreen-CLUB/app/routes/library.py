
from flask import Blueprint, request, jsonify, session, current_app,flash,redirect,url_for
from models import db, tblmovies, tbltv
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import and_,or_,any_
from datetime import date
import requests

library_bp = Blueprint("library", __name__)


@library_bp.route("/api/Library/movie")
def get_libraryMovies():
    if "user_id" not in session:
        return jsonify({
            "error": "Please login first"
        }), 401
    user_id = session["user_id"]
    stmt = db.select(tblmovies).where(tblmovies.user_id == user_id)
    libraryMovies = db.session.execute(stmt).scalars().all()
    movies = []

    for movie in libraryMovies:
        movies.append({
            "tmdb_id": movie.tmdb_id,
            "title": movie.title,
            "poster_path": movie.poster_path,
            "release_date": (movie.release_date.isoformat() if movie.release_date else None),
            "overview": movie.overview,
            "popularity": movie.popularity,
            "vote_average": movie.vote_average,
            "vote_count": movie.vote_count,
            "library_status": movie.library_status,
            "status": movie.status,
            "media_type": "movie"
        })

    return jsonify({"libraryMovies": movies})    



@library_bp.route("/api/Library/tv")
def get_libraryTv():
    if "user_id" not in session:
        return jsonify({
            "error": "Please login first"
        }), 401
    
    user_id = session["user_id"]

    
    stmt = db.select(tbltv).where(tbltv.user_id == user_id)
    libraryTV = db.session.execute(stmt).scalars().all() 
    tvs = []

    for tv in libraryTV:

        tvs.append({
            "tmdb_id": tv.tmdb_id,
            "title": tv.title,
            "poster_path": tv.poster_path,
            "release_date": (tv.first_air_date.isoformat() if tv.first_air_date else None),
            "overview": tv.overview,
            "popularity": tv.popularity,
            "vote_average": tv.vote_average,
            "vote_count": tv.vote_count,
            "library_status": tv.library_status,
            "status": tv.status,
            "media_type": "tv"
        })

    return jsonify({"libraryTV": tvs})    


@library_bp.route("/api/addToLibrary", methods=["POST"])
def add_library():

    if "user_id" not in session:
        return jsonify({
            "error": "Session expired. Please login again."
        }), 401

    user_id = session["user_id"]

    # Read JSON
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON data"
        }), 400

    # Extract fields
    tmdb_id = data.get("tmdb_id")
    title = data.get("title")
    poster_path = data.get("poster_path")
    release_date = data.get("release_date")
    overview = data.get("overview")
    popularity = data.get("popularity")
    vote_average = data.get("vote_average")
    vote_count = data.get("vote_count")
    media_type = data.get("media_type")

    # Validate important fields
    if media_type not in ("movie", "tv"):
        return jsonify({
            "error": "Invalid media type"
        }), 400

    if type(tmdb_id) is not int or tmdb_id <= 0:
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


    if media_type == "movie":

        library = tblmovies(
            tmdb_id=tmdb_id,
            user_id=user_id,
            title=title,
            poster_path=poster_path,
            release_date=release_date,
            overview=overview,
            popularity=popularity,
            vote_average=vote_average,
            vote_count=vote_count,
            library_status=True
        )

    elif media_type == "tv":

        library = tbltv(
            tmdb_id=tmdb_id,
            user_id=user_id,
            title=title,
            poster_path=poster_path,
            first_air_date=release_date,
            overview=overview,
            popularity=popularity,
            vote_average=vote_average,
            vote_count=vote_count,
            library_status=True
        )

    try:
        db.session.add(library)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Added to library successfully!"
        }), 201

    except IntegrityError as error:
        db.session.rollback()

        constraint_name = getattr(
            getattr(error.orig, "diag", None),
            "constraint_name",
            None
        )

        if constraint_name in ("uq_movie_user_title", "uq_tv_user_title"):
            return jsonify({
                "error": "Already in your library"
            }), 409

        current_app.logger.exception("Library integrity error")

        return jsonify({
            "error": "Database constraint error"
        }), 500

    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Could not add item to library")

        return jsonify({
            "error": "Database error while adding to library"
        }), 500




@library_bp.route("/api/updateStatus", methods=["PATCH"])
def update_status():

    if "user_id" not in session:
        return jsonify({
            "error": "Session expired. Please login again."
        }), 401

    user_id = session["user_id"]

    # Read JSON
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON data"
        }), 400

    # Extract fields
    tmdb_id = data.get("tmdb_id")
    media_type = data.get("media_type").strip()
    status = data.get("new_status").strip()



    # Validate important fields
    if media_type not in ("movie", "tv"):
        return jsonify({
            "error": "Invalid media type"
        }), 400

    if type(tmdb_id) is not int or tmdb_id <= 0:
        return jsonify({
            "error": "Invalid TMDB ID"
        }), 400



    if media_type == "movie":
        stmt = db.select(tblmovies).where(and_(tblmovies.user_id == user_id,tblmovies.tmdb_id==tmdb_id))
        library = db.session.execute(stmt).scalar_one_or_none()

        if library:
            try:

                library.status = status
                db.session.commit()

                return jsonify({
                    "success": True,
                    "message": "updated successfully!"
                }), 200

            except SQLAlchemyError:
                db.session.rollback()
                current_app.logger.exception("Could not update item from library")

            return jsonify({
                "error": "Database error while updating"
            }), 500
        else:
            return jsonify({
                "error": "could not find item"
            }),404                        

    elif media_type == "tv":
        stmt = db.select(tbltv).where(and_(tbltv.user_id == user_id,tbltv.tmdb_id==tmdb_id))
        library = db.session.execute(stmt).scalar_one_or_none()

        if library:
            try:

                library.status = status
                db.session.commit()

                return jsonify({
                    "success": True,
                    "message": "updated successfully!"
                }), 200

            except SQLAlchemyError:
                db.session.rollback()
                current_app.logger.exception("Could not update item from library")

            return jsonify({
                "error": "Database error while updating"
            }), 500
        else:
            return jsonify({
                "error": "could not find item"
            }),404    

@library_bp.route("/api/removefromLibrary", methods=["DELETE"])
def remove_library():

    if "user_id" not in session:
        return jsonify({
            "error": "Session expired. Please login again."
        }), 401

    user_id = session["user_id"]

    # Read JSON
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON data"
        }), 400

    # Extract fields
    tmdb_id = data.get("tmdb_id")
    media_type = data.get("media_type")

    # Validate important fields
    if media_type not in ("movie", "tv"):
        return jsonify({
            "error": "Invalid media type"
        }), 400

    if type(tmdb_id) is not int or tmdb_id <= 0:
        return jsonify({
            "error": "Invalid TMDB ID"
        }), 400



    if media_type == "movie":
        stmt = db.select(tblmovies).where(and_(tblmovies.user_id == user_id,tblmovies.tmdb_id==tmdb_id))
        library = db.session.execute(stmt).scalar_one_or_none()

        if library:
            try:
                db.session.delete(library)
                db.session.commit()

                return jsonify({
                    "success": True,
                    "message": "removed from library successfully!"
                }), 200

            except SQLAlchemyError:
                db.session.rollback()
                current_app.logger.exception("Could not remove item from library")

                return jsonify({
                    "error": "Database error while adding to library"
                }), 500 
        else:
            return jsonify({
                "error": "could not find item"
            }),404                        

    elif media_type == "tv":
        stmt = db.select(tbltv).where(and_(tbltv.user_id == user_id,tbltv.tmdb_id==tmdb_id))
        library = db.session.execute(stmt).scalar_one_or_none()

        if library:
            try:
                db.session.delete(library)
                db.session.commit()

                return jsonify({
                    "success": True,
                    "message": "removed from library successfully!"
                }), 200

            except SQLAlchemyError:
                db.session.rollback()
                current_app.logger.exception("Could not remove item from library")

                return jsonify({
                    "error": "Database error while adding to library"
                }), 500 
        else:
            return jsonify({
                "error": "could not find item"
            }),404         