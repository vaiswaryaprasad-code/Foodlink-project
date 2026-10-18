from django.core.mail import send_mail
from django.conf import settings


def send_claim_email(donation, ngo):

    subject = "Food Donation Claimed Successfully"

    message = f"""
Hello {donation.donor.first_name or donation.donor.username},

Your donation has been claimed.

Food:
{donation.food_name}

Claimed by:
{ngo.ngoprofile.ngo_name}

Thank you for helping reduce food waste.

Regards,
FoodLink
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [donation.donor.email],
        fail_silently=False,
    )