from unittest.mock import Mock, patch

from flask import Flask

from app.extensions import cache
from app.services.tmdb_cache import get_cached_tmdb


def test_tmdb_caching():

    test_app = Flask(__name__)

    test_app.config.update(
        TESTING=True,
        CACHE_TYPE="SimpleCache",
        CACHE_DEFAULT_TIMEOUT=300
    )

    cache.init_app(test_app)

    with test_app.app_context():

        fake_response = Mock()

        fake_response.json.return_value = {
            "results": [{"id": 550, "title": "Test Movie"}]
        }

        with patch(
            "app.services.tmdb_cache.Config.tmdb_session.get",
            return_value=fake_response
        ) as mock_get:

            url = "https://api.themoviedb.org/3/discover/movie"

            params_page1 = (("page", 1),)
            params_page2 = (("page", 2),)

            # First call: cache miss
            result1 = get_cached_tmdb(url, params_page1)

            # Second call: cache hit
            result2 = get_cached_tmdb(url, params_page1)

            # Different parameters: cache miss
            result3 = get_cached_tmdb(url, params_page2)

            assert result1 == result2

            assert result3["results"][0]["title"] == "Test Movie"

            # Only two TMDB requests should have occurred
            assert mock_get.call_count == 2