"""
This module contains the RoomConverter class for converting room names.
"""

from werkzeug.exceptions import NotFound
from werkzeug.routing import BaseConverter

from .models import Room


class RoomConverter(BaseConverter):
    """
    Converter class for converting room names to database rooms and vice versa.
    """

    def to_python(self, value):
        """
        Converts a room name to a database room object.

        Args:
            value (str): The name of the room.

        Returns:
            Room: The corresponding database room object.

        Raises:
            NotFound: If the room does not exist in the database.
        """
        db_room = Room.query.filter_by(room_name=value).first()
        if db_room is None:
            raise NotFound
        return db_room

    def to_url(self, value):
        """
        Converts a database room object to its corresponding room name.

        Args:
            value (Room): The database room object.

        Returns:
            str: The name of the room.
        """
        return value.room_name
