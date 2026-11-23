import pytest
from app import create_app
from unittest.mock import MagicMock

@pytest.fixture
def app():

    app = create_app()

    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False
    )

    return app


@pytest.fixture
def client(app):

    return app.test_client()

from unittest.mock import MagicMock
import pytest


@pytest.fixture
def mock_db():

    connection = MagicMock()
    cursor = MagicMock()

    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor

    return connection, cursor