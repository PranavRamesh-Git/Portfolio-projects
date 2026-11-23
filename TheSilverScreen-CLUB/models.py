
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


def utcnow():
    return datetime.now(timezone.utc)


class users(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    fullname = db.Column(db.String(255), nullable=False)
    phoneNo = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    connections = db.Column(ARRAY(db.Integer), default=list)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    screenProfiles = db.relationship(
        "screenProfiles", back_populates="user", uselist=False, passive_deletes=True
    )
    movies = db.relationship("tblmovies", back_populates="user", passive_deletes=True)
    tv_shows = db.relationship("tbltv", back_populates="user", passive_deletes=True)
    notifications = db.relationship("notifications",back_populates="user",passive_deletes=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class tblmovies(db.Model):
    __tablename__ = "tblmovies"

    movie_id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    title = db.Column(db.String(200), nullable=False)
    poster_path = db.Column(db.Text)
    release_date = db.Column(db.Date)
    overview = db.Column(db.Text)
    popularity = db.Column(db.Float)
    vote_average = db.Column(db.Float)
    vote_count = db.Column(db.Integer)
    library_status = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.String(20), nullable=True)
    added_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "tmdb_id", name="uq_movie_user_title"),
        db.CheckConstraint(
            "status IN ('CURRENTLY WATCHING', 'DROPPED', 'FINISHED', 'WATCHLIST', 'NEXT WATCH', 'FAVORITE', 'IN LIBRARY')",
            name="chk_movie_status",
        ),
    )

    user = db.relationship("users", back_populates="movies")


class tbltv(db.Model):
    __tablename__ = "tbltv"

    tv_id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    title = db.Column(db.String(200), nullable=False)
    poster_path = db.Column(db.Text)
    first_air_date = db.Column(db.Date)
    overview = db.Column(db.Text)
    popularity = db.Column(db.Float)
    vote_average = db.Column(db.Float)
    vote_count = db.Column(db.Integer)
    library_status = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.String(20), nullable=True)
    added_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "tmdb_id", name="uq_tv_user_title"),
        db.CheckConstraint(
            "status IN ('CURRENTLY WATCHING', 'DROPPED', 'FINISHED', 'WATCHLIST', 'NEXT WATCH', 'FAVORITE', 'IN LIBRARY')",
            name="chk_tv_status",
        ),
    )

    user = db.relationship("users", back_populates="tv_shows")


class screenProfiles(db.Model):
    """One row per user. Column names match the form's name="" attributes."""
    __tablename__ = "screenProfiles"

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    )

    # Favourites
    comfort_watch = db.Column(db.String(200))
    quote_movie = db.Column(db.String(200))
    erase_memory = db.Column(db.String(200))
    soundtrack = db.Column(db.String(200))
    fav_actor = db.Column(db.String(200))
    fav_actress = db.Column(db.String(200))
    fav_villian = db.Column(db.String(200))
    fav_director = db.Column(db.String(100))
    cinephile_origin = db.Column(db.String(200))
    genres = db.Column(ARRAY(db.String(30)), default=list)

    # Opinions
    overrated = db.Column(db.String(200))
    underrated = db.Column(db.String(200))
    guilty_pleasure = db.Column(db.String(200))
    book_vs_movie = db.Column(db.String(20))
    watch_style = db.Column(db.String(20))
    subtitles = db.Column(db.String(20))
    theatre_seat = db.Column(db.String(20))
    snack = db.Column(db.String(30))
    spoiler_tolerance = db.Column(db.SmallInteger)
    cried = db.Column(db.String(200))
    plot_twist = db.Column(db.String(200))
    recommend = db.Column(db.Text)

    updated_at = db.Column(
        db.DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    __table_args__ = (
        db.CheckConstraint(
            "spoiler_tolerance BETWEEN 0 AND 10", name="ck_profile_spoiler_range"
        ),
    )

    user = db.relationship("users", back_populates="screenProfiles")


class connectionRequest(db.Model):
    __tablename__ = "connectionRequest"

    connection_id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    status = db.Column(db.String(20), default="PENDING", nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    __table_args__ = (
        db.CheckConstraint(
            "status IN ('PENDING', 'ACCEPTED', 'DECLINED')",
            name="chk_conn_status",
        ),
        db.CheckConstraint("requester_id <> receiver_id",name="chk_no_self_connection"),
        db.Index("uq_connection_pair",db.func.least(requester_id, receiver_id),db.func.greatest(requester_id, receiver_id),unique=True),
    )                   


class recommendations(db.Model):
    __tablename__ = "recommendations"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(
        db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    receiver_id = db.Column(
        db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    media_type = db.Column(db.String(10),nullable=False)        
    recommendation_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    poster_path = db.Column(db.Text)
    release_date = db.Column(db.Date)
    overview = db.Column(db.Text)
    popularity = db.Column(db.Float)
    vote_average = db.Column(db.Float)
    vote_count = db.Column(db.Integer) 
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    __table_args__ = (
        db.CheckConstraint(
            "sender_id <> receiver_id",
            name="chk_no_self_recommendation"
        ),

        db.CheckConstraint(
            "media_type IN ('movie', 'tv')",
            name="chk_recommendation_media_type"
        ),
    )

class notifications(db.Model):
    __tablename__ = "notifications"

    notification_id = db.Column(db.Integer, primary_key=True)

    connection_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "connectionRequest.connection_id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False
    )

    notif_type = db.Column(db.String(20), nullable=True)

    message = db.Column(db.Text, nullable=False)

    sent_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        nullable=False
    )

    user = db.relationship("users", back_populates="notifications")

    connection = db.relationship("connectionRequest")

class vw_recommendations(db.Model):
    __tablename__ = "vw_recommendations"

    id = db.Column(db.Integer, primary_key=True)

    sender_id = db.Column(db.Integer)
    sender_username = db.Column(db.String)
    sender_fullname = db.Column(db.String)

    receiver_id = db.Column(db.Integer)
    receiver_username = db.Column(db.String)
    receiver_fullname = db.Column(db.String)

    media_type = db.Column(db.String(10))
    recommendation_id = db.Column(db.Integer)

    created_at = db.Column(db.DateTime(timezone=True))

    title = db.Column(db.String(200))
    poster_path = db.Column(db.Text)
    release_date = db.Column(db.Date)

    overview = db.Column(db.Text)
    popularity = db.Column(db.Float)
    vote_average = db.Column(db.Float)
    vote_count = db.Column(db.Integer)