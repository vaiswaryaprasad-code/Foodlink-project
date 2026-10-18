
from django.utils import timezone
from donor.models import FoodDonation


def check_expired_food():
    """
    Mark donations as expired when their expiry time has passed.

    Claimed donations retain their claim records, but their
    donation status is updated to Expired.
    """

    now = timezone.now()

    expired_food = FoodDonation.objects.filter(
        expiry_time__lte=now
    ).exclude(
        status="Expired"
    )

    updated_count = expired_food.update(
        status="Expired",
        food_status="Unsafe",
        food_safety_score=0,
        priority_score=0
    )

    return updated_count

