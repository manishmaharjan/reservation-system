# PWP SPRING 2024

# Room Booking system at the University

# Group information

- Student 1. Manish Maharjan and mmaharja@student.oulu.fi
- Student 2. Manex Sorarrain and manex.sorarrainagirrezabala@student.oulu.fi
- Student 3. Amael Kesteman and amael.kesteman@student.oulu.fi

**Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client**

## Deliverable 2 - Database

In this deriverable we have added some new files, which contain the information to define our models, create a database and to populate it. The db file is instance/reservation_system.db.

The used libraries are located at requirements.txt and can be installed with

```
pip install -r requirements.txt
```

We used a SQLite database, specifically the sqlite3 3.37.2 version. The documentation used to create the models can be found [here](https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/)

Finally, to set up the database we first have to run the app with the next command:

```

export FLASK_APP=api  # For Linux/Mac
set FLASK_APP=api      # For Windows Command Prompt
export FLASK_DEBUG=1
export FLASK_ENV=development

# debugging in mac

-pysqlite3 is likely already installed as a default in mac and would be throwing error during pip installation

-install globally by deactivating venv
pip install flask-sqlalchemy
activate venv

cd src/
flask run
```

After that, to populate the database we will have to run the population script with the following command:

```
python populationScript.py
```

After that, our database will be created and populated with a few ins``tances of each model.

To see those instances, w``e can run the following lines in a python console.

```
from models import Room,Reservation,User, db
from app import app
ctx = app.app_context()
ctx.push()
db.create_all()
Room.query.first()
```

With that last line a Room object called 'Room 1' should be retrieved.
