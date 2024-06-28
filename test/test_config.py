from src.api import app
import tempfile
from src import db
from population_script import populate_db
import os
import pytest
from src.models import User, ApiKey

@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.config["TESTING"] = True

    with app.app_context():
        populate_db(test = True)
        yield app.test_client()

    os.close(db_fd)
    os.unlink(db_fname)

