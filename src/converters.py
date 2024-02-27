from werkzeug.routing import BaseConverter
from src.models import Room
from werkzeug.exceptions import NotFound

class RoomConverter(BaseConverter):
    def to_python(self, room_name):
        db_room = Room.query.filter_by(room_name=room_name).first()
        if db_room is None:
            raise NotFound
        return db_room
        
    def to_url(self, db_room):
        return db_room.room_name