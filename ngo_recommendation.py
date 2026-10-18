
from math import radians, sin, cos, sqrt, atan2
from ngo.models import NGOProfile


# ==========================================
# Calculate Distance Between Two Locations
# ==========================================
def calculate_distance(lat1, lon1, lat2, lon2):

    R = 6371  # Earth's radius in kilometers

    lat1 = radians(float(lat1))
    lon1 = radians(float(lon1))
    lat2 = radians(float(lat2))
    lon2 = radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    # Protect against floating-point rounding errors.
    a = max(0, min(1, a))

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


# ==========================================
# NGO Recommendation Based on Distance
# ==========================================

def recommend_ngo(donation):

    # Get approved and verified NGOs with valid coordinates.
    ngos = NGOProfile.objects.filter(
        user__is_approved=True,
        user__verification_status="VERIFIED",
        latitude__isnull=False,
        longitude__isnull=False
    ).select_related("user")

    if not ngos.exists():
        return None

    if donation.latitude is None or donation.longitude is None:
        return None

    best_ngo = None
    shortest_distance = float("inf")

    for ngo in ngos:

        try:
            food_lat = float(donation.latitude)
            food_lon = float(donation.longitude)
            ngo_lat = float(ngo.latitude)
            ngo_lon = float(ngo.longitude)
        except (TypeError, ValueError):
            continue

        # Skip invalid coordinates.
        if not (-90 <= food_lat <= 90):
            continue
        if not (-180 <= food_lon <= 180):
            continue
        if not (-90 <= ngo_lat <= 90):
            continue
        if not (-180 <= ngo_lon <= 180):
            continue

        distance = calculate_distance(
            food_lat,
            food_lon,
            ngo_lat,
            ngo_lon
        )

        if distance < shortest_distance:
            shortest_distance = distance
            best_ngo = ngo

    # recommended_ngo is a CharField, so return the username.
    if best_ngo:
        return best_ngo.user.username

    return None




# ==========================================
# Nearest Food Recommendation for an NGO
# ==========================================
def recommend_nearest_food(ngo, donations):

    if ngo.latitude is None or ngo.longitude is None:
        return None

    nearest_food = None
    shortest_distance = float("inf")

    for donation in donations:

        if donation.latitude is None or donation.longitude is None:
            continue

        try:
            distance = calculate_distance(
                ngo.latitude,
                ngo.longitude,
                donation.latitude,
                donation.longitude
            )
        except (TypeError, ValueError):
            continue

        if distance < shortest_distance:
            shortest_distance = distance
            nearest_food = donation

    if nearest_food:
        nearest_food.distance = round(shortest_distance, 2)

    return nearest_food

