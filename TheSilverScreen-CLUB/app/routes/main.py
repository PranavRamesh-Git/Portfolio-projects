from flask import Flask, Blueprint,redirect,render_template,url_for,request,jsonify,flash,session
from models import db,users,tblmovies,tbltv,screenProfiles,notifications
import math
import psycopg
from psycopg.errors import UniqueViolation
from datetime import date,datetime,timedelta
from config import Config
import requests


main_bp = Blueprint("main",__name__)



@main_bp.route('/TSSclub/home')
def home():
    if "user_id" not in session:
        flash("Please login again, session expired", "error")
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]  
    genresTV = []
    genres = []
    try:
        url = f"{Config.TMDB_BASE_URL}/genre/movie/list"
        response = Config.tmdb_session.get(url,headers=Config.HEADERS,params=Config.params,timeout=10)
        response.raise_for_status()
        data = response.json()
        genres = data.get("genres",[])

        url = f"{Config.TMDB_BASE_URL}/genre/tv/list"
        response = Config.tmdb_session.get(url,headers=Config.HEADERS,params=Config.params,timeout=10)
        response.raise_for_status()
        data = response.json()
        genresTV = data.get("genres",[])




    except requests.exceptions.RequestException as e:
        print("Error occurred: ",e)
        genres = []
        genresTV = []


    stmt = db.select(screenProfiles).where(screenProfiles.user_id == user_id)
    profile = db.session.execute(stmt).scalar_one_or_none()
    
    stmt = db.select(users).where(users.user_id == user_id)
    user = db.session.execute(stmt).scalar_one_or_none()

    return render_template("home.html", genres = genres,genresTV=genresTV,profile = profile,user = user)

