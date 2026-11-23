from app.extensions import cache
from config import Config


@cache.memoize(timeout=300)
def get_cached_tmdb(url, params_tuple):

    params = dict(params_tuple)

    print("CALLING TMDB API")

    response = Config.tmdb_session.get(
        url,
        headers=Config.HEADERS,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()