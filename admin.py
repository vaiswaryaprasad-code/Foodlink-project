from django.contrib import admin
from .models import NGOProfile, FoodClaim


@admin.register(NGOProfile)
class NGOProfileAdmin(admin.ModelAdmin):
    list_display = (
        "ngo_name",
        "city",
        "latitude",
        "longitude",
        "capacity",
        "reliability_score",
        "successful_claims",
    )

    search_fields = (
        "ngo_name",
        "city",
    )


@admin.register(FoodClaim)
class FoodClaimAdmin(admin.ModelAdmin):
    list_display = (
        "donation",
        "ngo",
        "claimed_at",
    )