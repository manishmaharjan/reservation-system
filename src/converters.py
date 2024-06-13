"""
This module contains the RoomConverter class for converting room names.
"""

from werkzeug.exceptions import NotFound
from werkzeug.routing import BaseConverter

from .models import Room


class RoomConverter(BaseConverter):
    """
    Converter class for converting room ids to database rooms and vice versa.
    """

    def to_python(self, value):
        """
        Converts a room id to a database room object.

        Args:
            value (int): The id of the room.

        Returns:
            Room: The corresponding database room object.

        Raises:
            NotFound: If the room does not exist in the database.
        """
        db_room = Room.query.filter_by(id=value).first()
        if db_room is None:
            raise NotFound
        return db_room

    def to_url(self, value):
        """
        Converts a database room object to its corresponding room id.

        Args:
            value (Room): The database room object.

        Returns:
            id: The id of the room.
        """
        return value.id
