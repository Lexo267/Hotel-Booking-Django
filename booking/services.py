import requests
import urllib3
import json
import os
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://hotelbooking.stepprojects.ge/api"
FALLBACK_FILE = "fallback_bookings.json"

# სარეზერვო მონაცემები (იმ შემთხვევისთვის, თუ აკადემიის სერვერი 504 შეცდომას აბრუნებს)
MOCK_HOTELS = [
    {
        "id": 1,
        "name": "Tbilisi Marriott Hotel",
        "address": "რუსთაველის გამზირი 13",
        "city": "Tbilisi",
        "featuredImage": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800"
    },
    {
        "id": 2,
        "name": "Radisson Blu Batumi",
        "address": "ნინოშვილის ქუჩა 1",
        "city": "Batumi",
        "featuredImage": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800"
    },
    {
        "id": 3,
        "name": "Rooms Hotel Kazbegi",
        "address": "ვ. გორგასლის ქუჩა 1",
        "city": "Stepantsminda",
        "featuredImage": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800"
    }
]

MOCK_ROOM_TYPES = [
    {"id": 1, "name": "Single Room"},
    {"id": 2, "name": "Double Room"},
    {"id": 3, "name": "Deluxe Room"}
]

MOCK_ROOMS = [
    {
        "id": 101,
        "name": "Standard Single Room",
        "hotelId": 1,
        "roomTypeId": 1,
        "pricePerNight": 180,
        "maximumGuests": 1,
        "images": [{"source": "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800"}]
    },
    {
        "id": 102,
        "name": "Executive Double Room",
        "hotelId": 1,
        "roomTypeId": 2,
        "pricePerNight": 290,
        "maximumGuests": 2,
        "images": [{"source": "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800"}]
    },
    {
        "id": 201,
        "name": "Sea View Deluxe Suite",
        "hotelId": 2,
        "roomTypeId": 3,
        "pricePerNight": 420,
        "maximumGuests": 3,
        "images": [{"source": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800"}]
    },
    {
        "id": 202,
        "name": "Cozy Double Room",
        "hotelId": 2,
        "roomTypeId": 2,
        "pricePerNight": 240,
        "maximumGuests": 2,
        "images": [{"source": "https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=800"}]
    },
    {
        "id": 301,
        "name": "Mountain View Deluxe",
        "hotelId": 3,
        "roomTypeId": 3,
        "pricePerNight": 380,
        "maximumGuests": 2,
        "images": [{"source": "https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=800"}]
    },
    {
        "id": 302,
        "name": "Alpine Single Room",
        "hotelId": 3,
        "roomTypeId": 1,
        "pricePerNight": 160,
        "maximumGuests": 1,
        "images": [{"source": "https://images.unsplash.com/photo-1505693314120-0d443867891c?w=800"}]
    }
]


def _load_local_bookings():
    if os.path.exists(FALLBACK_FILE):
        with open(FALLBACK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_local_bookings(bookings):
    with open(FALLBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(bookings, f, ensure_ascii=False, indent=2)


class HotelBookingAPI:
    """სერვის კლასი IT Step Academy-ის API-სთან სამუშაოდ (ავტომატური Fallback მხარდაჭერით)"""

    @staticmethod
    def get_all_hotels():
        try:
            response = requests.get(f"{BASE_URL}/Hotels/GetAll", verify=False, timeout=8)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return MOCK_HOTELS

    @staticmethod
    def get_cities():
        try:
            response = requests.get(f"{BASE_URL}/Hotels/GetCities", verify=False, timeout=8)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return sorted(list({h["city"] for h in MOCK_HOTELS}))

    @staticmethod
    def get_hotel_by_id(hotel_id):
        try:
            response = requests.get(f"{BASE_URL}/Hotels/GetHotel/{hotel_id}", verify=False, timeout=8)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return next((h for h in MOCK_HOTELS if str(h["id"]) == str(hotel_id)), None)

    @staticmethod
    def get_all_rooms():
        try:
            response = requests.get(f"{BASE_URL}/Rooms/GetAll", verify=False, timeout=8)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return [dict(r) for r in MOCK_ROOMS]

    @staticmethod
    def get_room_types():
        try:
            response = requests.get(f"{BASE_URL}/Rooms/GetRoomTypes", verify=False, timeout=8)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return MOCK_ROOM_TYPES

    @staticmethod
    def filter_rooms(room_type_id=None, price_from=None, price_to=None, check_in=None, check_out=None):
        payload = {}
        if room_type_id:
            payload["roomTypeId"] = int(room_type_id)
        if price_from:
            payload["priceFrom"] = float(price_from)
        if price_to:
            payload["priceTo"] = float(price_to)
        if check_in:
            payload["checkIn"] = check_in
        if check_out:
            payload["checkOut"] = check_out

        try:
            response = requests.post(f"{BASE_URL}/Rooms/GetFiltered", json=payload, verify=False, timeout=8)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass

        # ლოკალური ფილტრაცია
        rooms = [dict(r) for r in MOCK_ROOMS]
        if room_type_id:
            rooms = [r for r in rooms if str(r["roomTypeId"]) == str(room_type_id)]
        if price_from:
            rooms = [r for r in rooms if r["pricePerNight"] >= float(price_from)]
        if price_to:
            rooms = [r for r in rooms if r["pricePerNight"] <= float(price_to)]
        if check_in and check_out:
            bookings = _load_local_bookings()
            booked_room_ids = set()
            for b in bookings:
                if not (check_out <= b["checkInDate"][:10] or check_in >= b["checkOutDate"][:10]):
                    booked_room_ids.add(b["roomID"])
            rooms = [r for r in rooms if r["id"] not in booked_room_ids]
        return rooms

    @staticmethod
    def get_all_bookings():
        try:
            response = requests.get(f"{BASE_URL}/Booking", verify=False, timeout=8)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return _load_local_bookings()

    @staticmethod
    def create_booking(room_id, check_in, check_out, customer_name, customer_phone):
        payload = {
            "roomID": int(room_id),
            "checkInDate": check_in,
            "checkOutDate": check_out,
            "totalPrice": 0,
            "isConfirmed": True,
            "customerName": customer_name,
            "customerPhone": customer_phone
        }
        try:
            response = requests.post(f"{BASE_URL}/Booking", json=payload, verify=False, timeout=8)
            if response.status_code in [200, 201]:
                return True, response.text
        except Exception:
            pass

        # ლოკალური ჯავშნის შენახვა
        bookings = _load_local_bookings()
        for b in bookings:
            if b["roomID"] == int(room_id):
                if not (check_out <= b["checkInDate"][:10] or check_in >= b["checkOutDate"][:10]):
                    return False, "ნომერი მითითებულ თარიღებში უკვე დაჯავშნილია."

        room = next((r for r in MOCK_ROOMS if r["id"] == int(room_id)), None)
        d1 = datetime.strptime(check_in, "%Y-%m-%d")
        d2 = datetime.strptime(check_out, "%Y-%m-%d")
        nights = max((d2 - d1).days, 1)
        total = nights * (room["pricePerNight"] if room else 100)

        new_id = max([b["id"] for b in bookings], default=0) + 1
        bookings.append({
            "id": new_id,
            "roomID": int(room_id),
            "checkInDate": check_in,
            "checkOutDate": check_out,
            "totalPrice": total,
            "isConfirmed": True,
            "customerName": customer_name,
            "customerPhone": customer_phone
        })
        _save_local_bookings(bookings)
        return True, "OK"

    @staticmethod
    def cancel_booking(booking_id):
        try:
            response = requests.delete(f"{BASE_URL}/Booking/{booking_id}", verify=False, timeout=8)
            if response.status_code in [200, 204]:
                return True
        except Exception:
            pass

        bookings = _load_local_bookings()
        updated = [b for b in bookings if str(b["id"]) != str(booking_id)]
        _save_local_bookings(updated)
        return True