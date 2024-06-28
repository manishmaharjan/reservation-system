from src.api import prepare_api
import tempfile
from src import db, create_app
from population_script import populate_db
import os
import pytest
from src.models import User, ApiKey

@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()

    app = create_app(test_config={
            "SQLALCHEMY_DATABASE_URI": f"sqlite:////home/manex/Documents/Adimen artifiziala/4/Programable web project/reservation-system/instance/tests.db",
            "TESTING": True
        })
    
    # Configure all the api
    prepare_api(app)
    
    with app.app_context() as app_ctx:
        app_ctx.push()
        populate_db(db,app_ctx, test= True)
        yield app.test_client()

    os.close(db_fd)
    os.unlink(db_fname)
        
