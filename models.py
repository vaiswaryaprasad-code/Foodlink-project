from django.db import models
from django.conf import settings
from donor.models import FoodDonation
from accounts.models import CustomUser


class FoodClaim(models.Model):
    donation = models.ForeignKey(
        FoodDonation,
        on_delete=models.CASCADE
    )

    ngo = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )

    claimed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ngo.username} claimed {self.donation.food_name}"
    
from django.db import models
from django.conf import settings


class NGOProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    ngo_name = models.CharField(max_length=100)

    address = models.CharField(
        max_length=255,
        default=""
    )

    city = models.CharField(
        max_length=100,
        default=""
    )

    latitude = models.FloatField(
        default=0
    )

    longitude = models.FloatField(
        default=0
    )

    capacity = models.IntegerField(
        default=100
    )

    reliability_score = models.IntegerField(
        default=80
    )

    successful_claims = models.IntegerField(
        default=0
    )

    def __str__(self):
        return self.ngo_name
    
