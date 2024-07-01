import argparse
import sys

from api.reservationClient import ReservationClient
from api.availabilityClient import AvailabilityClient
from api.reservationClient import ReservationClient
from api.userClient import UserClient

# Function definitions for each CLI command


def create_user(args):
    """
    Command: create_user
    Creates a new user with the provided username and email.

    Arguments:
    --username: Username of the new user (required)
    --email: Email of the new user (required)
    """
    username = args.username
    email = args.email
    result = UserClient.create_user(username, email)
    print(result)


def get_user(args):
    """
    Command: get_user
    Retrieves details of a user with the given user_id and api_key.

    Arguments:
    --user_id: ID of the user (required)
    --api_key: API key for authentication (required)
    """
    user_id = args.user_id
    api_key = args.api_key
    result = UserClient.get_user(user_id, api_key)
    print(result)


def update_user(args):
    """
    Command: update_user
    Updates details of a user with the given user_id, api_key, username, and email.

    Arguments:
    --user_id: ID of the user (required)
    --username: New username (optional)
    --email: New email (optional)
    --api_key: API key for authentication (required)
    """
    user_id = args.user_id
    username = args.username
    email = args.email
    api_key = args.api_key
    result = UserClient.update_user(user_id, api_key, username, email)
    print(result)


def delete_user(args):
    """
    Command: delete_user
    Deletes a user with the given user_id and api_key.

    Arguments:
    --user_id: ID of the user (required)
    --api_key: API key for authentication (required)
    """
    user_id = args.user_id
    api_key = args.api_key
    result = UserClient.delete_user(user_id, api_key)
    print(result)


def create_reservation(args):
    """
    Command: create_reservation
    Creates a new reservation with the provided user_id, room_id, date, start_time, end_time, and api_key.

    Arguments:
    --user_id: ID of the user (required)
    --room_id: ID of the room (required)
    --date: Reservation date in YYYY-MM-DD format (required)
    --start_time: Start time of the reservation in HH:MM format (required)
    --end_time: End time of the reservation in HH:MM format (required)
    --api_key: API key for authentication (required)
    """
    user_id = args.user_id
    room_id = args.room_id
    date = args.date
    start_time = args.start_time
    end_time = args.end_time
    api_key = args.api_key
    result = ReservationClient.create_reservation(
        user_id, room_id, date, start_time, end_time, api_key
    )
    print(result)


def get_reservations(args):
    """
    Command: get_reservations
    Retrieves all reservations of a user with the given user_id and api_key.

    Arguments:
    --user_id: ID of the user (required)
    --api_key: API key for authentication (required)
    """
    user_id = args.user_id
    api_key = args.api_key
    result = ReservationClient.get_reservations(user_id, api_key)
    print(result)


def get_reservation(args):
    """
    Command: get_reservation
    Retrieves details of a specific reservation with the given user_id, reservation_id, and api_key.

    Arguments:
    --user_id: ID of the user (required)
    --reservation_id: ID of the reservation (required)
    --api_key: API key for authentication (required)
    """
    user_id = args.user_id
    reservation_id = args.reservation_id
    api_key = args.api_key
    result = ReservationClient.get_reservation(user_id, reservation_id, api_key)
    print(result)


def update_reservation(args):
    """
    Command: update_reservation
    Updates details of a reservation with the given user_id, reservation_id, date, start_time, end_time, room_id, and api_key.

    Arguments:
    --user_id: ID of the user (required)
    --reservation_id: ID of the reservation (required)
    --date: New date for the reservation in YYYY-MM-DD format (optional)
    --start_time: New start time for the reservation in HH:MM format (optional)
    --end_time: New end time for the reservation in HH:MM format (optional)
    --room_id: New ID of the room (optional)
    --api_key: API key for authentication (required)
    """
    user_id = args.user_id
    reservation_id = args.reservation_id
    date = args.date
    start_time = args.start_time
    end_time = args.end_time
    room_id = args.room_id
    api_key = args.api_key
    result = ReservationClient.put_reservation(
        user_id, reservation_id, api_key, date, start_time, end_time, room_id
    )
    print(result)


def delete_reservation(args):
    """
    Command: delete_reservation
    Deletes a reservation with the given user_id, reservation_id, and api_key.

    Arguments:
    --user_id: ID of the user (required)
    --reservation_id: ID of the reservation (required)
    --api_key: API key for authentication (required)
    """
    user_id = args.user_id
    reservation_id = args.reservation_id
    api_key = args.api_key
    result = ReservationClient.delete_reservation(user_id, reservation_id, api_key)
    print(result)


def get_available_rooms(args):
    """
    Command: get_available_rooms
    Retrieves available rooms for the specified date, time, and duration.

    Arguments:
    --date: Date for checking room availability in YYYY-MM-DD format (required)
    --time: Time for checking room availability in HH:MM format (required)
    --duration: Optional duration of the reservation in minutes
    """
    date = args.date
    time = args.time
    duration = args.duration
    result = AvailabilityClient.get_available_rooms(date, time, duration)
    print(result)


def main():
    # Create the main argument parser
    parser = argparse.ArgumentParser(
        description="Command Line Interface for Room Reservation API"
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(
        title="Commands", description="Available commands"
    )

    # User commands
    parser_create_user = subparsers.add_parser("create_user", help="Create a new user")
    parser_create_user.add_argument(
        "--username", required=True, help="Username of the new user"
    )
    parser_create_user.add_argument(
        "--email", required=True, help="Email of the new user"
    )
    parser_create_user.set_defaults(func=create_user)

    parser_get_user = subparsers.add_parser("get_user", help="Get user details")
    parser_get_user.add_argument(
        "--user_id", required=True, type=int, help="ID of the user"
    )
    parser_get_user.add_argument(
        "--api_key", required=True, help="API key for authentication"
    )
    parser_get_user.set_defaults(func=get_user)

    parser_update_user = subparsers.add_parser(
        "update_user", help="Update user details"
    )
    parser_update_user.add_argument(
        "--user_id", required=True, type=int, help="ID of the user"
    )
    parser_update_user.add_argument("--username", help="New username")
    parser_update_user.add_argument("--email", help="New email")
    parser_update_user.add_argument(
        "--api_key", required=True, help="API key for authentication"
    )
    parser_update_user.set_defaults(func=update_user)

    parser_delete_user = subparsers.add_parser("delete_user", help="Delete a user")
    parser_delete_user.add_argument(
        "--user_id", required=True, type=int, help="ID of the user"
    )
    parser_delete_user.add_argument(
        "--api_key", required=True, help="API key for authentication"
    )
    parser_delete_user.set_defaults(func=delete_user)

    # Reservation commands
    parser_create_reservation = subparsers.add_parser(
        "create_reservation", help="Create a new reservation"
    )
    parser_create_reservation.add_argument(
        "--user_id", required=True, type=int, help="ID of the user"
    )
    parser_create_reservation.add_argument(
        "--room_id", required=True, type=int, help="ID of the room"
    )
    parser_create_reservation.add_argument(
        "--date", required=True, help="Reservation date (YYYY-MM-DD)"
    )
    parser_create_reservation.add_argument(
        "--start_time", required=True, help="Start time of the reservation (HH:MM)"
    )
    parser_create_reservation.add_argument(
        "--end_time", required=True, help="End time of the reservation (HH:MM)"
    )
    parser_create_reservation.add_argument(
        "--api_key", required=True, help="API key for authentication"
    )
    parser_create_reservation.set_defaults(func=create_reservation)

    parser_get_reservations = subparsers.add_parser(
        "get_reservations", help="Get all reservations of a user"
    )
    parser_get_reservations.add_argument(
        "--user_id", required=True, type=int, help="ID of the user"
    )
    parser_get_reservations.add_argument(
        "--api_key", required=True, help="API key for authentication"
    )
    parser_get_reservations.set_defaults(func=get_reservations)

    parser_get_reservation = subparsers.add_parser(
        "get_reservation", help="Get details of a specific reservation"
    )
    parser_get_reservation.add_argument(
        "--user_id", required=True, type=int, help="ID of the user"
    )
    parser_get_reservation.add_argument(
        "--reservation_id", required=True, type=int, help="ID of the reservation"
    )
    parser_get_reservation.add_argument(
        "--api_key", required=True, help="API key for authentication"
    )
    parser_get_reservation.set_defaults(func=get_reservation)

    parser_update_reservation = subparsers.add_parser(
        "update_reservation", help="Update details of a reservation"
    )
    parser_update_reservation.add_argument(
        "--user_id", required=True, type=int, help="ID of the user"
    )
    parser_update_reservation.add_argument(
        "--reservation_id", required=True, type=int, help="ID of the reservation"
    )
    parser_update_reservation.add_argument(
        "--date", help="New date for the reservation (YYYY-MM-DD)"
    )
    parser_update_reservation.add_argument(
        "--start_time", help="New start time for the reservation (HH:MM)"
    )
    parser_update_reservation.add_argument(
        "--end_time", help="New end time for the reservation (HH:MM)"
    )
    parser_update_reservation.add_argument(
        "--room_id", type=int, help="New room ID for the reservation"
    )
    parser_update_reservation.add_argument(
        "--api_key", required=True, help="API key for authentication"
    )
    parser_update_reservation.set_defaults(func=update_reservation)

    parser_delete_reservation = subparsers.add_parser(
        "delete_reservation", help="Delete a reservation"
    )
    parser_delete_reservation.add_argument(
        "--user_id", required=True, type=int, help="ID of the user"
    )
    parser_delete_reservation.add_argument(
        "--reservation_id", required=True, type=int, help="ID of the reservation"
    )
    parser_delete_reservation.add_argument(
        "--api_key", required=True, help="API key for authentication"
    )
    parser_delete_reservation.set_defaults(func=delete_reservation)

    parser_get_available_rooms = subparsers.add_parser(
        "get_available_rooms", help="Get available rooms"
    )
    parser_get_available_rooms.add_argument(
        "--date", required=True, help="Date for checking room availability (YYYY-MM-DD)"
    )
    parser_get_available_rooms.add_argument(
        "--time", required=True, help="Time for checking room availability (HH:MM)"
    )
    parser_get_available_rooms.add_argument(
        "--duration", type=int, help="Optional duration of the reservation in minutes"
    )
    parser_get_available_rooms.set_defaults(func=get_available_rooms)

    # Parse arguments and execute the appropriate function
        # Parse arguments and execute the appropriate function
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
