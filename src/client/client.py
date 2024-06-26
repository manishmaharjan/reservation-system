import argparse
from api.reservationClient import ReservationClient
from api.availabilityClient import AvailabilityClient
from api.userClient import UserClient


def create_user(args):
    username = args.username
    email = args.email
    result = UserClient.create_user(username, email)
    print(result)

def get_user(args):
    user_id = args.user_id
    api_key = args.api_key
    result = UserClient.get_user(user_id, api_key)
    print(result)

def update_user(args):
    user_id = args.user_id
    username = args.username
    email = args.email
    api_key = args.api_key
    result = UserClient.update_user(user_id, api_key, username, email )
    print(result)

def delete_user(args):
    user_id = args.user_id
    api_key = args.api_key
    result = UserClient.delete_user(user_id, api_key)
    print(result)

def create_reservation(args):
    user_id = args.user_id
    room_id = args.room_id
    date = args.date
    start_time = args.start_time
    end_time = args.end_time
    api_key = args.api_key
    result = ReservationClient.create_reservation(user_id, room_id, date, start_time, end_time, api_key)
    print(result)

def get_reservations(args):
    user_id = args.user_id
    api_key = args.api_key
    result = ReservationClient.get_reservations(user_id, api_key)
    print(result)

def get_reservation(args):
    user_id = args.user_id
    reservation_id = args.reservation_id
    api_key = args.api_key
    result = ReservationClient.get_reservation(user_id, reservation_id, api_key)
    print(result)

def update_reservation(args):
    user_id = args.user_id
    reservation_id = args.reservation_id
    date = args.date
    start_time = args.start_time
    end_time = args.end_time
    room_id = args.room_id
    api_key = args.api_key
    result = ReservationClient.put_reservation(user_id, reservation_id, api_key, date, start_time, end_time, room_id)
    print(result)

def delete_reservation(args):
    user_id = args.user_id
    reservation_id = args.reservation_id
    api_key = args.api_key
    result = ReservationClient.delete_reservation(user_id, reservation_id, api_key)
    print(result)

def get_available_rooms(args):
    date = args.date
    time = args.time
    duration = args.duration
    result = AvailabilityClient.get_available_rooms(date, time, duration)
    print(result)

def main():
    parser = argparse.ArgumentParser(description="Command Line Interface for Room Reservation API")

    subparsers = parser.add_subparsers(title="Commands", description="Available commands")

    # User commands
    parser_create_user = subparsers.add_parser('create_user', help="Create a new user")
    parser_create_user.add_argument('--username', required=True, help="Username of the new user")
    parser_create_user.add_argument('--email', required=True, help="Email of the new user")
    parser_create_user.set_defaults(func=create_user)

    parser_get_user = subparsers.add_parser('get_user', help="Get user details")
    parser_get_user.add_argument('--user_id', required=True, type=int, help="ID of the user")
    parser_get_user.add_argument('--api_key', required=True, help="API key for authentication")
    parser_get_user.set_defaults(func=get_user)

    parser_update_user = subparsers.add_parser('update_user', help="Update user details")
    parser_update_user.add_argument('--user_id', required=True, type=int, help="ID of the user")
    parser_update_user.add_argument('--username', help="New username")
    parser_update_user.add_argument('--email', help="New email")
    parser_update_user.add_argument('--api_key', required=True, help="API key for authentication")
    parser_update_user.set_defaults(func=update_user)

    parser_delete_user = subparsers.add_parser('delete_user', help="Delete a user")
    parser_delete_user.add_argument('--user_id', required=True, type=int, help="ID of the user")
    parser_delete_user.add_argument('--api_key', required=True, help="API key for authentication")
    parser_delete_user.set_defaults(func=delete_user)

    # Reservation commands
    parser_create_reservation = subparsers.add_parser('create_reservation', help="Create a new reservation")
    parser_create_reservation.add_argument('--user_id', required=True, type=int, help="ID of the user")
    parser_create_reservation.add_argument('--room_id', required=True, type=int, help="ID of the room")
    parser_create_reservation.add_argument('--date', required=True, help="Reservation date (YYYY-MM-DD)")
    parser_create_reservation.add_argument('--start_time', required=True, help="Start time of the reservation (HH:MM)")
    parser_create_reservation.add_argument('--end_time', required=True, help="End time of the reservation (HH:MM)")
    parser_create_reservation.add_argument('--api_key', required=True, help="API key for authentication")
    parser_create_reservation.set_defaults(func=create_reservation)

    parser_get_reservations = subparsers.add_parser('get_reservations', help="Get all reservations of a user")
    parser_get_reservations.add_argument('--user_id', required=True, type=int, help="ID of the user")
    parser_get_reservations.add_argument('--api_key', required=True, help="API key for authentication")
    parser_get_reservations.set_defaults(func=get_reservations)

    parser_get_reservation = subparsers.add_parser('get_reservation', help="Get details of a specific reservation")
    parser_get_reservation.add_argument('--user_id', required=True, type=int, help="ID of the user")
    parser_get_reservation.add_argument('--reservation_id', required=True, type=int, help="ID of the reservation")
    parser_get_reservation.add_argument('--api_key', required=True, help="API key for authentication")
    parser_get_reservation.set_defaults(func=get_reservation)

    parser_update_reservation = subparsers.add_parser('update_reservation', help="Update details of a reservation")
    parser_update_reservation.add_argument('--user_id', required=True, type=int, help="ID of the user")
    parser_update_reservation.add_argument('--reservation_id', required=True, type=int, help="ID of the reservation")
    parser_update_reservation.add_argument('--date', help="New date for the reservation (YYYY-MM-DD)")
    parser_update_reservation.add_argument('--start_time', help="New start time for the reservation (HH:MM)")
    parser_update_reservation.add_argument('--end_time', help="New end time for the reservation (HH:MM)")
    parser_update_reservation.add_argument('--room_id', type=int, help="New room ID for the reservation")
    parser_update_reservation.add_argument('--api_key', required=True, help="API key for authentication")
    parser_update_reservation.set_defaults(func=update_reservation)

    parser_delete_reservation = subparsers.add_parser('delete_reservation', help="Delete a reservation")
    parser_delete_reservation.add_argument('--user_id', required=True, type=int, help="ID of the user")
    parser_delete_reservation.add_argument('--reservation_id', required=True, type=int, help="ID of the reservation")
    parser_delete_reservation.add_argument('--api_key', required=True, help="API key for authentication")
    parser_delete_reservation.set_defaults(func=delete_reservation)

    parser_get_available_rooms = subparsers.add_parser('get_available_rooms', help="Get available rooms")
    parser_get_available_rooms.add_argument('--date', required=True, help="Date for checking room availability (YYYY-MM-DD)")
    parser_get_available_rooms.add_argument('--time', required=True, help="Time for checking room availability (HH:MM)")
    parser_get_available_rooms.add_argument('--duration', type=int, help="Optional duration of the reservation in minutes")
    parser_get_available_rooms.set_defaults(func=get_available_rooms)


    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()