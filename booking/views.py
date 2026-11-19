from django.shortcuts import render, redirect
from django.contrib import messages
from .services import HotelBookingAPI


def home_view(request):
    """მთავარი გვერდი (Home) - ფავორიტი ნომრების გამოტანა"""
    all_rooms = HotelBookingAPI.get_all_rooms()
    favorite_rooms = all_rooms[:6]  # პირველი 6 გამორჩეული ნომერი
    return render(request, 'booking/index.html', {
        'favorite_rooms': favorite_rooms
    })


def hotels_view(request):
    """სასტუმროების გვერდი (Hotels) - ქალაქების მიხედვით ფილტრაციით"""
    hotels = HotelBookingAPI.get_all_hotels()
    cities = HotelBookingAPI.get_cities()
    selected_city = request.GET.get('city', '').strip()

    if selected_city:
        hotels = [h for h in hotels if h.get('city', '').lower() == selected_city.lower()]

    return render(request, 'booking/hotels.html', {
        'hotels': hotels,
        'cities': cities,
        'selected_city': selected_city
    })


def rooms_view(request):
    """ნომრების გვერდი (Rooms) - ფილტრაცია (ტიპი, ფასი, თარიღები) და დაჯავშნა"""
    room_types = HotelBookingAPI.get_room_types()
    hotels = HotelBookingAPI.get_all_hotels()
    hotels_map = {h['id']: h for h in hotels}

    # დაჯავშნის მოთხოვნის დამუშავება (POST)
    if request.method == 'POST':
        room_id = request.POST.get('room_id')
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        customer_name = request.POST.get('customer_name', '').strip()
        customer_phone = request.POST.get('customer_phone', '').strip()

        if not all([room_id, check_in, check_out, customer_name, customer_phone]):
            messages.error(request, "გთხოვთ შეავსოთ ყველა სავალდებულო ველი!")
        elif check_in >= check_out:
            messages.error(request, "გასვლის თარიღი (Check-out) უნდა იყოს შესვლის თარიღზე (Check-in) გვიან!")
        else:
            success, msg = HotelBookingAPI.create_booking(
                room_id, check_in, check_out, customer_name, customer_phone
            )
            if success:
                messages.success(request, "ნომერი წარმატებით დაიჯავშნა!")
                return redirect('booked_rooms')
            else:
                messages.error(request, f"დაჯავშნა ვერ მოხერხდა (შესაძლოა ნომერი ამ თარიღებში დაკავებულია). დეტალები: {msg}")

    # ფილტრის პარამეტრების წაკითხვა (GET)
    hotel_id = request.GET.get('hotel_id', '').strip()
    room_type_id = request.GET.get('room_type', '').strip()
    price_from = request.GET.get('price_from', '').strip()
    price_to = request.GET.get('price_to', '').strip()
    check_in = request.GET.get('check_in', '').strip()
    check_out = request.GET.get('check_out', '').strip()

    # თუ რომელიმე ფილტრი გამოყენებულია
    if any([room_type_id, price_from, price_to, check_in, check_out]):
        rooms = HotelBookingAPI.filter_rooms(
            room_type_id=room_type_id or None,
            price_from=price_from or None,
            price_to=price_to or None,
            check_in=check_in or None,
            check_out=check_out or None
        )
    else:
        rooms = HotelBookingAPI.get_all_rooms()

    # კონკრეტულ სასტუმროზე დაკლიკებისას გაფილტვრა
    selected_hotel = None
    if hotel_id:
        rooms = [r for r in rooms if str(r.get('hotelId')) == str(hotel_id)]
        selected_hotel = hotels_map.get(int(hotel_id)) if hotel_id.isdigit() else None

    # თითოეულ ნომერს მივაბათ სასტუმროს სახელი და ქალაქი
    for room in rooms:
        hotel_info = hotels_map.get(room.get('hotelId'), {})
        room['hotel_name'] = hotel_info.get('name', 'უცნობი სასტუმრო')
        room['hotel_city'] = hotel_info.get('city', '')

    return render(request, 'booking/rooms.html', {
        'rooms': rooms,
        'room_types': room_types,
        'selected_hotel': selected_hotel,
        'filters': {
            'hotel_id': hotel_id,
            'room_type': room_type_id,
            'price_from': price_from,
            'price_to': price_to,
            'check_in': check_in,
            'check_out': check_out,
        }
    })


def booked_rooms_view(request):
    """დაჯავშნილი ნომრების გვერდი (Booked Rooms) - ცხრილი, ფილტრი ქალაქით და გაუქმება"""
    if request.method == 'POST' and 'cancel_booking_id' in request.POST:
        booking_id = request.POST.get('cancel_booking_id')
        if HotelBookingAPI.cancel_booking(booking_id):
            messages.success(request, "ჯავშანი წარმატებით გაუქმდა!")
        else:
            messages.error(request, "ჯავშნის გაუქმება ვერ მოხერხდა.")
        return redirect('booked_rooms')

    bookings = HotelBookingAPI.get_all_bookings()
    hotels = HotelBookingAPI.get_all_hotels()
    rooms = HotelBookingAPI.get_all_rooms()
    cities = HotelBookingAPI.get_cities()

    hotels_map = {h['id']: h for h in hotels}
    rooms_map = {r['id']: r for r in rooms}

    enriched_bookings = []
    for b in bookings:
        room = rooms_map.get(b.get('roomID'), {})
        hotel = hotels_map.get(room.get('hotelId'), {})

        # სურათების უსაფრთხოდ ამოღება
        hotel_img = hotel.get('featuredImage') or (hotel.get('images')[0]['source'] if hotel.get('images') else '')
        room_img = room.get('images')[0]['source'] if room.get('images') else ''

        enriched_bookings.append({
            'id': b.get('id'),
            'hotel_name': hotel.get('name', 'სასტუმრო'),
            'hotel_city': hotel.get('city', 'უცნობი'),
            'hotel_image': hotel_img,
            'room_name': room.get('name', f"ნომერი #{b.get('roomID')}"),
            'room_image': room_img,
            'price_per_night': room.get('pricePerNight', 0),
            'customer_name': b.get('customerName', ''),
            'customer_phone': b.get('customerPhone', ''),
            'status': 'დადასტურებული' if b.get('isConfirmed') else 'მოლოდინში',
            'check_in': str(b.get('checkInDate', ''))[:10],
            'check_out': str(b.get('checkOutDate', ''))[:10],
            'total_price': b.get('totalPrice', 0),
        })

    selected_city = request.GET.get('city', '').strip()
    if selected_city:
        enriched_bookings = [
            item for item in enriched_bookings
            if item['hotel_city'].lower() == selected_city.lower()
        ]

    return render(request, 'booking/booked.html', {
        'bookings': enriched_bookings,
        'cities': cities,
        'selected_city': selected_city
    })