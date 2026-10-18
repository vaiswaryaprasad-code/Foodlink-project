from donor.models import FoodDonation


def get_best_food():
    """
    AI ranks food using Priority Score
    """

    donations = FoodDonation.objects.filter(
        status="Available"
    ).order_by("-priority_score", "expiry_time")

    return donations