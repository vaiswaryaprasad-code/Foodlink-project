from django.utils import timezone


def calculate_priority(donation):

    score = 0

    # ----------------------------
    # 1. Expiry Time (0–50 points)
    # ----------------------------
    hours = (
        donation.expiry_time - timezone.now()
    ).total_seconds() / 3600

    if hours <= 2:
        score += 50
    elif hours <= 6:
        score += 40
    elif hours <= 12:
        score += 30
    elif hours <= 24:
        score += 20
    else:
        score += 10

    # ----------------------------
    # 2. Food Safety (0–20 points)
    # ----------------------------
    score += donation.food_safety_score * 0.20

    # ----------------------------
    # 3. Quantity (0–15 points)
    # ----------------------------
    if donation.quantity >= 20:
        score += 15
    elif donation.quantity >= 10:
        score += 10
    elif donation.quantity >= 5:
        score += 5

    # ----------------------------
    # 4. Donor Reliability (0–15 points)
    # ----------------------------
    score += donation.donor.reliability_score * 0.15

    # Maximum score = 100
    if score > 100:
        score = 100

    return int(score)