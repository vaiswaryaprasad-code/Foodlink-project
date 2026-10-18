from django.utils import timezone


def calculate_food_safety(prepared_time, expiry_time):
    """
    Calculate a time-based food safety risk score.

    This is a basic decision-support estimate, not a guarantee
    that food is safe to consume.
    """

    now = timezone.now()

    # 1. Check whether time values are available
    if not prepared_time or not expiry_time:
        return 0, "Unsafe"

    # 2. Ensure datetime values are timezone-aware
    if timezone.is_naive(prepared_time):
        prepared_time = timezone.make_aware(prepared_time)

    if timezone.is_naive(expiry_time):
        expiry_time = timezone.make_aware(expiry_time)

    # 3. Reject expired food
    if expiry_time <= now:
        return 0, "Unsafe"

    # 4. Reject invalid preparation times
    if prepared_time > now:
        return 0, "Unsafe"

    if expiry_time <= prepared_time:
        return 0, "Unsafe"

    # 5. Calculate time differences in hours
    hours_since_prepared = (
        now - prepared_time
    ).total_seconds() / 3600

    total_shelf_life = (
        expiry_time - prepared_time
    ).total_seconds() / 3600

    hours_until_expiry = (
        expiry_time - now
    ).total_seconds() / 3600

    # 6. Calculate the percentage of shelf life already used
    if total_shelf_life > 0:
        shelf_life_used = (
            hours_since_prepared / total_shelf_life
        ) * 100
    else:
        shelf_life_used = 100

    # 7. Calculate a gradually decreasing score
    score = 100 - (shelf_life_used * 0.7)

    # Additional penalty as expiry approaches
    if hours_until_expiry <= 2:
        score -= 25
    elif hours_until_expiry <= 6:
        score -= 15
    elif hours_until_expiry <= 12:
        score -= 5

    # 8. Keep the score between 0 and 100
    score = round(max(0, min(100, score)))

    # 9. Determine the status
    if score >= 80:
        status = "Safe"
    elif score >= 50:
        status = "Moderate Risk"
    else:
        status = "Unsafe"

    return score, status