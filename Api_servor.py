from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)

# Configuration for SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reservation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy database object
db = SQLAlchemy(app)

# Initialize Flask-Restful Api
api = Api(app)

# Import and register resources
from resources import RegisterUser, GetReservations, CreateReservation, DeleteReservation

api.add_resource(RegisterUser, '/register')
api.add_resource(GetReservations, '/reservations')
api.add_resource(CreateReservation, '/reservation/<int:room>')
api.add_resource(DeleteReservation, '/reservation/<int:room>/<int:reservation_id>')

if __name__ == '__main__':
    # Create database tables
    db.create_all()

    # Run the Flask app
    app.run(debug=True)
