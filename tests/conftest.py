import pytest
import os
import sys

# Ensure mysterymart project directory is in Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, Product, FAQ, User
from seed import seed_database


@pytest.fixture(scope='session')
def app():
    """Create application configured for testing with in-memory SQLite database."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        seed_database()
        yield app
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()
