from flask import Blueprint, request, jsonify,session,flash,redirect,url_for,current_app
from config import Config
import requests
from models import db, tblmovies, tbltv
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import date
from app.services.tmdb_cache import get_cached_tmdb

discover_bp = Blueprint("discover", __name__)




@discover_bp.route("/api/movies")
def get_movies():


    if "user_id" not in session:
        return jsonify({"error": "Session expired"}), 401

    user_id = session["user_id"]

    search = request.args.get("search", "").strip()
    genre = request.args.get("genre", "").strip()
    page = request.args.get("page", 1, type=int)

    # Validate page
    if page is None or page < 1 or page > 500:
        return jsonify({"error": "Invalid page number"}), 400

    # Validate search
    if len(search) > 100:
        return jsonify({"error": "Search is too long"}), 400

    # Validate multiple genres
    selected_genres = set()

    if genre:
        genre_ids = genre.split("|")

        if not all(g.isdigit() for g in genre_ids):
            return jsonify({"error": "Invalid genres"}), 400

        selected_genres = set(map(int, genre_ids))

    # Common TMDB parameters
    params = {
        "page": page
    }

    # Choose TMDB endpoint
    if search:
        url = f"{Config.TMDB_BASE_URL}/search/movie"
        params["query"] = search

    else:
        url = f"{Config.TMDB_BASE_URL}/discover/movie"

        if genre:
            params["with_genres"] = genre

    try:

        data = get_cached_tmdb(url,tuple(sorted(params.items())))

        results = data.get("results", [])

        # When searching by title, additionally
        # filter the current result page by genre
        if search and selected_genres:

            filtered_results = []

            for movie in results:
                movie_genres = movie.get("genre_ids", [])

                for g in selected_genres:
                    if g in movie_genres:
                        filtered_results.append(movie)
                        break

            results = filtered_results

        # Convert TMDB results to frontend format
        allMovies = []

        for item in results:

            poster = item.get("poster_path")

            if poster:
                poster_path = (
                    f"https://image.tmdb.org/t/p/w500{poster}"
                )
            else:
                poster_path = "/static/img/NA.png"

            movie = {
                "tmdb_id": item.get("id"),
                "title": item.get("title") or "NA",
                "release_date": item.get("release_date") or "TBA",
                "overview": item.get("overview") or "NIL",
                "original_language": item.get("original_language") or "NA",
                "popularity": item.get("popularity", 0),
                "poster_path": poster_path,
                "vote_average": item.get("vote_average", 0),
                "vote_count": item.get("vote_count", 0),
                "media_type": "movie"
            }

            allMovies.append(movie)

        # Retrieve user's saved movie IDs
        stmt = db.select(tblmovies.tmdb_id).where(
            tblmovies.user_id == user_id
        )

        library_tmdb_ids = db.session.execute(stmt).scalars().all()

        mymovies = []

        for tmdb_id in library_tmdb_ids:
            mymovies.append({
                "tmdb_id": tmdb_id
            })

        # Return JSON to JavaScript
        return jsonify({
            "allMovies": allMovies,
            "mymovies": mymovies,
            "page": data.get("page", page),
            "total_pages": min(data.get("total_pages", 1), 500),
            "total_results": data.get("total_results", 0)
        })

    except requests.exceptions.RequestException:
        current_app.logger.exception("TMDB request failed")

        return jsonify({
            "error": "Could not retrieve movies from TMDB"
        }), 503


@discover_bp.route("/api/TV")
def get_tv():

    if "user_id" not in session:
        return jsonify({"error": "Session expired"}), 401

    user_id = session["user_id"]

    # Get query parameters
    search = request.args.get("searchTV", "").strip()
    genre = request.args.get("genreTV", "").strip()
    page = request.args.get("page", 1, type=int)

    # Validate page
    if page is None or page < 1 or page > 500:
        return jsonify({"error": "Invalid page number"}), 400

    # Validate search
    if len(search) > 100:
        return jsonify({"error": "Search is too long"}), 400

    # Validate multiple genres
    selected_genres = set()

    if genre:
        genre_ids = genre.split("|")

        if not all(g.isdigit() for g in genre_ids):
            return jsonify({"error": "Invalid genres"}), 400

        selected_genres = set(map(int, genre_ids))

    # Common TMDB parameters
    params = {
        "page": page,
        "include_null_first_air_dates": "false"
    }


    # Choose TMDB endpoint
    if search:
        url = f"{Config.TMDB_BASE_URL}/search/tv"
        params["query"] = search

    else:
        url = f"{Config.TMDB_BASE_URL}/discover/tv"

        if genre:
            params["with_genres"] = genre


    try:
        data = get_cached_tmdb(url,tuple(sorted(params.items())))

        results = data.get("results", [])

        # When searching by title, additionally
        # filter the current result page by genre
        if search and selected_genres:

            filtered_results = []

            for tv in results:
                tv_genres = tv.get("genre_ids", [])

                for g in selected_genres:
                    if g in tv_genres:
                        filtered_results.append(tv)
                        break

            results = filtered_results

        # Convert TMDB results to frontend format
        allTV = []
        for item in results:

            poster = item.get("poster_path")

            poster_path = (
                f"https://image.tmdb.org/t/p/w500{poster}"
                if poster
                else "/static/img/NA.png"
            )

            tv = {
                "tmdb_id": item.get("id"),
                "title": item.get("name") or "NA",
                "release_date": item.get("first_air_date") or "TBA",
                "overview": item.get("overview") or "NIL",
                "original_language": item.get("original_language") or "NA",
                "popularity": item.get("popularity", 0),
                "poster_path": poster_path,
                "vote_average": item.get("vote_average", 0),
                "vote_count": item.get("vote_count", 0),
                "media_type": "tv"
            }

            allTV.append(tv)

        # Retrieve user's saved movie IDs
        stmt = db.select(tbltv.tmdb_id).where(
            tbltv.user_id == user_id
        )

        library_tv_tmdb_ids = db.session.execute(stmt).scalars().all()

        mytvs = []

        for tmdb_id in library_tv_tmdb_ids:
            mytvs.append({
                "tmdb_id": tmdb_id
            })

        # Return JSON to JavaScript
        return jsonify({
            "allTV": allTV,
            "mytvs": mytvs,
            "page": data.get("page", page),
            "total_pages": min(data.get("total_pages", 1), 500),
            "total_results": data.get("total_results", 0)
        })

    except requests.exceptions.RequestException:
        current_app.logger.exception("TMDB request failed")

        return jsonify({
            "error": "Could not retrieve movies from TMDB"
        }), 503



@discover_bp.route("/api/trending/movies")
def get_trendingMovies():
    if "user_id" not in session:
        return jsonify({
            "error": "Session expired. Please login again."
        }), 401
    
    user_id = session["user_id"]
    url = f"{Config.TMDB_BASE_URL}/trending/movie/day" 

    duration = request.args.get('duration','')
    if duration == "day":
        url = f"{Config.TMDB_BASE_URL}/trending/movie/day" 
    elif duration == "week":
        url = f"{Config.TMDB_BASE_URL}/trending/movie/week" 

    params = {
        "language" : "en-US"
    }

    try:
        data = get_cached_tmdb(url,tuple(sorted(params.items())))

 
        trendingMovies = []

        for item in data.get("results", []):

            poster = item.get("poster_path")

            poster_path = (
                f"https://image.tmdb.org/t/p/w500{poster}"
                if poster
                else "/static/img/NA.png"
            )

            movie = {
                "tmdb_id": item.get("id"),
                "title": item.get("title") or "NA",
                "release_date": item.get("release_date") or "TBA",
                "overview": item.get("overview") or "NIL",
                "original_language": item.get("original_language") or "NA",
                "popularity": item.get("popularity", 0),
                "poster_path": poster_path,
                "vote_average": item.get("vote_average", 0),
                "vote_count": item.get("vote_count", 0),
                "media_type": "movie"
            }

            trendingMovies.append(movie)


            stmt = db.select(tblmovies).where(tblmovies.user_id == user_id)
            libraryMovies = db.session.execute(stmt).scalars().all()
            mymovies = []

            for movie in libraryMovies:
                mymovies.append({
                    "tmdb_id": movie.tmdb_id,
                    "title": movie.title,
                    "poster_path": movie.poster_path,
                    "release_date": movie.release_date,
                    "overview": movie.overview,
                    "popularity": movie.popularity,
                    "vote_average": movie.vote_average,
                    "vote_count": movie.vote_count,
                    "library_status": movie.library_status,
                    "status": movie.status,
                    "media_type": "movie"
                })


        return jsonify({
            "trendingMovies": trendingMovies,
            "mymovies": mymovies
        })

    except requests.exceptions.RequestException:
        discover_bp.logger if False else None
        return jsonify({
            "error": "Could not retrieve movies from TMDB"
        }), 503


@discover_bp.route("/api/trending/tv")
def get_trendingTV():
    if "user_id" not in session:
        return jsonify({
            "error": "Session expired. Please login again."
        }), 401

    user_id = session["user_id"]
    
    url = f"{Config.TMDB_BASE_URL}/trending/tv/day" 

    duration = request.args.get('duration','')
    if duration == "day":
        url = f"{Config.TMDB_BASE_URL}/trending/tv/day" 
    elif duration == "week":
        url = f"{Config.TMDB_BASE_URL}/trending/tv/week" 

    params = {
        "language" : "en-US"
    }

    try:
        data = get_cached_tmdb(url,tuple(sorted(params.items())))

        trendingTV = []

        for item in data.get("results", []):

            poster = item.get("poster_path")

            poster_path = (
                f"https://image.tmdb.org/t/p/w500{poster}"
                if poster
                else "/static/img/NA.png"
            )

            tv = {
                "tmdb_id": item.get("id"),
                "title": item.get("name") or "NA",
                "release_date": item.get("first_air_date") or "TBA",
                "overview": item.get("overview") or "NIL",
                "original_language": item.get("original_language") or "NA",
                "popularity": item.get("popularity", 0),
                "poster_path": poster_path,
                "vote_average": item.get("vote_average", 0),
                "vote_count": item.get("vote_count", 0),
                "media_type": "tv"
            }

            trendingTV.append(tv)
            stmt = db.select(tbltv).where(tbltv.user_id == user_id)
            libraryTV = db.session.execute(stmt).scalars().all() 
            mytvs = []

            for tv in libraryTV:
                mytvs.append({
                    "tmdb_id": tv.tmdb_id,
                    "title": tv.title,
                    "poster_path": tv.poster_path,
                    "release_date": tv.first_air_date,
                    "overview": tv.overview,
                    "popularity": tv.popularity,
                    "vote_average": tv.vote_average,
                    "vote_count": tv.vote_count,
                    "library_status": tv.library_status,
                    "status": tv.status,
                    "media_type": "tv"
                })

        return jsonify({
            "trendingTV": trendingTV,
            "mytvs": mytvs
        })

    except requests.exceptions.RequestException:
        discover_bp.logger if False else None
        return jsonify({
            "error": "Could not retrieve movies from TMDB"
        }), 503