from flask_restful import Api
from src import create_app, db
from .resources import reservation, user
from src.converters import RoomConverter
app = create_app()

api = Api(app)

app.url_map.converters["room"] = RoomConverter

api.add_resource(user.RegisterUser, "/api/user/register/")
api.add_resource(reservation.GetReservations, "/api/reservations/")
api.add_resource(reservation.CreateReservation, "/api/reservations/<room:room>/")
api.add_resource(reservation.DeleteReservation, '/api/reservations/<room:room>/<int:reservation_id>/')
api.add_resource(reservation.GetReservationList, '/api/reservations/list/')
