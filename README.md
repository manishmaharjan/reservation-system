# PWP SPRING 2024
# Room Booking system at the University
# Group information
* Student 1. Manish Maharjan and mmaharja@student.oulu.fi
* Student 2. Manex Sorarrain and manex.sorarrainagirrezabala@student.oulu.fi
* Student 3. Amael Kesteman and amael.kesteman@student.oulu.fi


__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__

## Deliverable 2 - Database
In this deriverable we have added some new files, which contain the information to define our models, create a database and to populate it. The db file is instance/reservation_system.db.

The used libraries are located at requirements.txt and can be installed with

```
pip install -r requirements.txt
```
We used a SQLite database, specifically the sqlite3 3.37.2 version. The documentation used to create the models can be found [here](https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/)

Finally, to set up the database we first have to run the app with the next command:
```
flask run
```
After that, to populate the database we will have to run the population script with the following command:
```
python populationScript.py 
```

After that, our database will be created and populated with a few instances of each model.
