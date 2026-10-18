
from django.utils import timezone


def calculate_priority(food):
    """
    Calculate a priority score for food donations.

    Higher score = higher collection priority.
    Expired food receives a score of 0.
    """

    now = timezone.now()

    # Expired donations must not receive collection priority.
    if not food.expiry_time or food.expiry_time <= now:
        return 0

    score = 0

    # 1. Food safety score: maximum 40 points
    safety_score = food.food_safety_score or 0
    score += max(0, min(100, safety_score)) * 0.4

    # 2. Remaining time before expiry: maximum 40 points
    remaining = (
        food.expiry_time - now
    ).total_seconds() / 3600

    if remaining <= 2:
        score += 40
    elif remaining <= 6:
        score += 30
    elif remaining <= 12:
        score += 20
    elif remaining <= 24:
        score += 10

    # 3. Quantity: maximum 20 points
    try:
        quantity = float(food.quantity or 0)
    except (TypeError, ValueError):
        quantity = 0

    if quantity >= 100:
        score += 20
    elif quantity >= 50:
        score += 15
    elif quantity >= 20:
        score += 10
    elif quantity > 0:
        score += 5

    return round(score, 2)

