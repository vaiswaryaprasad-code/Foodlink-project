
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable


def get_coordinates(address):
    """
    Get latitude and longitude for a given address.
    Returns (latitude, longitude) or (None, None).
    """

    if not address or not address.strip():
        print("Geocoding Error: Address is empty.")
        return None, None

    geolocator = Nominatim(
        user_agent="foodlink_app",
        timeout=10
    )

    try:
        location = geolocator.geocode(
            address,
            country_codes="in"
        )

        if location:
            print("Location found:", location.address)
            print("Latitude:", location.latitude)
            print("Longitude:", location.longitude)

            return location.latitude, location.longitude

        print("Location not found:", address)

    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        print("Geocoding service unavailable:", e)

    except Exception as e:
        print("Geocoding Error:", e)

    return None, None

