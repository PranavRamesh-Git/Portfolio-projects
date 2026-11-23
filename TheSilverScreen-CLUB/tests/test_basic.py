

def test_movie_data():
    movie = {
        "tmdb_id": 550,
        "title": "Fight Club",
        "media_type": "movie"
    }

    assert movie["tmdb_id"] == 550
    assert movie["media_type"] == "movie"