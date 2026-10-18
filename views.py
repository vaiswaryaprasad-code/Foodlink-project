
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField
from django.utils import timezone

from accounts.decorators import ngo_required
from donor.models import FoodDonation
from .models import FoodClaim, NGOProfile

from ai_engine.expiry_manager import check_expired_food
from ai_engine.ngo_recommendation import (
    recommend_nearest_food
)
from ai_engine.email_service import send_claim_email


# ==========================================
# NGO DASHBOARD
# ==========================================

@login_required
@ngo_required
def dashboard(request):

    # 1. Update expired donations
    check_expired_food()

    # 2. Fetch available, unexpired, safe food
    available_food = FoodDonation.objects.filter(
        status="Available",
        expiry_time__gt=timezone.now(),
        food_status__in=["Safe", "Moderate Risk"]
    ).order_by(
        Case(
            When(food_status="Safe", then=Value(1)),
            When(food_status="Moderate Risk", then=Value(2)),
            default=Value(3),
            output_field=IntegerField(),
        ),
        "-food_safety_score",
        "-priority_score",
        "expiry_time",
        "-created_at"
    )

    # 3. Highest-ranked food
    best_food = available_food.first()

    # 4. Get the logged-in NGO profile
    ngo_profile = get_object_or_404(
        NGOProfile,
        user=request.user
    )

    # 5. Find the nearest available food donation
    nearest_food = recommend_nearest_food(
        ngo_profile,
        available_food
    )

    # 6. Get this NGO's claim history
    my_claims = FoodClaim.objects.filter(
        ngo=request.user
    ).order_by("-claimed_at")

    recent_claims = my_claims[:5]

    # 7. Dashboard statistics
    context = {
        "available_food": available_food,
        "best_food": best_food,
        "nearest_food": nearest_food,
        "my_claims": my_claims,
        "total_available": available_food.count(),
        "total_claims": my_claims.count(),

        "claimed_food": FoodDonation.objects.filter(
            status="Claimed"
        ).count(),

        "expired_food": FoodDonation.objects.filter(
            status="Expired"
        ).count(),

        "recent_claims": recent_claims,
    }

    return render(
        request,
        "ngo/dashboard.html",
        context
    )


# ==========================================
# AVAILABLE FOOD
# ==========================================

@login_required
@ngo_required
def available_food(request):

    # Update expired donations
    check_expired_food()

    # Get available and unexpired donations
    donations = FoodDonation.objects.filter(
        status="Available",
        expiry_time__gt=timezone.now()
    ).order_by(
        "-priority_score",
        "-food_safety_score",
        "expiry_time",
        "-created_at"
    )

    return render(
        request,
        "ngo/available_food.html",
        {
            "donations": donations
        }
    )


# ==========================================
# CLAIM FOOD
# ==========================================


@login_required
@ngo_required
def claim_food(request, id):

    print("\n========== CLAIM FOOD DEBUG ==========")
    print("Request method:", request.method)
    print("Logged-in user:", request.user.username)
    print("User type:", request.user.user_type)
    print("Donation ID:", id)

    # Claims must use POST
    if request.method != "POST":
        print("STOPPED: Request is not POST")

        messages.warning(
            request,
            "Please use the Claim button to claim food."
        )
        return redirect("ngo_dashboard")

    # Update expired donations
    print("Checking expired donations...")

    check_expired_food()

    # Find donation
    try:
        donation = FoodDonation.objects.get(id=id)
    except FoodDonation.DoesNotExist:
        print("STOPPED: Donation does not exist")

        messages.error(
            request,
            "Food donation not found."
        )
        return redirect("ngo_dashboard")

    print("Food name:", donation.food_name)
    print("Donation status:", donation.status)
    print("Expiry time:", donation.expiry_time)
    print("Current time:", timezone.now())

    # Check expiry
    if donation.expiry_time <= timezone.now():
        print("STOPPED: Food has expired")

        messages.error(
            request,
            "This food has expired and cannot be claimed."
        )
        return redirect("ngo_dashboard")

    # Check availability
    if donation.status != "Available":
        print("STOPPED: Food is not available")

        messages.warning(
            request,
            f"This food is not available. Current status: {donation.status}"
        )
        return redirect("ngo_dashboard")

    # Check duplicate claims
    if FoodClaim.objects.filter(donation=donation).exists():
        print("STOPPED: A claim already exists")

        messages.warning(
            request,
            "This food has already been claimed."
        )
        return redirect("ngo_dashboard")

    # Create claim
    print("Creating FoodClaim record...")

    try:
        FoodClaim.objects.create(
            donation=donation,
            ngo=request.user
        )

        print("FoodClaim record created successfully")

    except Exception as e:
        print("ERROR CREATING CLAIM:", repr(e))

        messages.error(
            request,
            "Unable to claim food. Please check the server error."
        )
        return redirect("ngo_dashboard")

    # Update donation status
    try:
        donation.status = "Claimed"
        donation.save(update_fields=["status"])

        print("Donation status updated:", donation.status)

    except Exception as e:
        print("ERROR UPDATING DONATION:", repr(e))

        messages.error(
            request,
            "The claim was created, but the donation status could not be updated."
        )
        return redirect("ngo_dashboard")

    # Send claim email
    try:
        send_claim_email(
            donation,
            request.user
        )
        print("Claim email sent successfully")

    except Exception as e:
        print("EMAIL ERROR:", repr(e))

    messages.success(
        request,
        f"{donation.food_name} claimed successfully."
    )

    print("CLAIM COMPLETED SUCCESSFULLY")
    print("======================================\n")

    return redirect("ngo_dashboard")




# ==========================================
# CLAIM HISTORY
# ==========================================

@login_required
@ngo_required
def claim_history(request):

    claims = FoodClaim.objects.filter(
        ngo=request.user
    ).order_by("-claimed_at")

    return render(
        request,
        "ngo/claim_history.html",
        {
            "claims": claims,
            "total": claims.count()
        }
    )


# ==========================================
# PICKUP FOOD
# ==========================================

@login_required
@ngo_required
def pickup_food(request, id):

    # Find this NGO's claim
    claim = get_object_or_404(
        FoodClaim,
        id=id,
        ngo=request.user
    )

    donation = claim.donation

    # Only claimed food can be picked up
    if donation.status != "Claimed":

        messages.warning(
            request,
            "Only claimed food can be marked as picked up."
        )

        return redirect("claim_history")

    # Mark as picked up
    donation.status = "Picked Up"

    donation.save(
        update_fields=["status"]
    )

    messages.success(
        request,
        "Food marked as Picked Up."
    )

    return redirect("claim_history")


# ==========================================
# DELIVER FOOD
# ==========================================

@login_required
@ngo_required
def deliver_food(request, id):

    # Find this NGO's claim
    claim = get_object_or_404(
        FoodClaim,
        id=id,
        ngo=request.user
    )

    donation = claim.donation

    # Food must be picked up first
    if donation.status != "Picked Up":

        messages.warning(
            request,
            "Food must be picked up before delivery."
        )

        return redirect("claim_history")

    # Mark as delivered
    donation.status = "Delivered"

    donation.save(
        update_fields=["status"]
    )

    messages.success(
        request,
        "Food delivered successfully."
    )

    return redirect("claim_history")


# ==========================================
# UPDATE STATUS
# ==========================================

@login_required
@ngo_required
def update_status(request, id):

    # Accept POST requests only
    if request.method != "POST":

        return redirect("claim_history")

    # Find this NGO's claim
    claim = get_object_or_404(
        FoodClaim,
        id=id,
        ngo=request.user
    )

    donation = claim.donation

    # Read the requested status
    status = request.POST.get("status")

    # Allowed status values
    allowed_statuses = [
        "Picked Up",
        "Delivered"
    ]

    # Validate status
    if status not in allowed_statuses:

        messages.error(
            request,
            "Invalid status selected."
        )

        return redirect("claim_history")

    # Validate pickup sequence
    if status == "Picked Up":

        if donation.status != "Claimed":

            messages.warning(
                request,
                "Food must be claimed before pickup."
            )

            return redirect("claim_history")

    # Validate delivery sequence
    elif status == "Delivered":

        if donation.status != "Picked Up":

            messages.warning(
                request,
                "Food must be picked up before delivery."
            )

            return redirect("claim_history")

    # Update the donation status
    donation.status = status

    donation.save(
        update_fields=["status"]
    )

    messages.success(
        request,
        f"Food status updated to {status}."
    )

    return redirect("claim_history")

# ==========================================
# UPDATE NGO PROFILE
# ==========================================


def update_profile(request):

    # Get the logged-in NGO's profile
    profile, created = NGOProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "ngo_name": request.user.username,
            "address": "",
            "city": "",
        }
    )

    if request.method == "POST":

        # Read updated form values
        ngo_name = request.POST.get("ngo_name", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        
        print("PROFILE UPDATE DEBUG")
        print("Request method:", request.method)
        print("Received NGO name:", repr(ngo_name))
        print("Received address:", repr(address))
        print("Received city:", repr(city))

        # Validate required fields
        if not ngo_name or not address or not city:
            messages.error(
                request,
                "Please fill in all required fields."
            )

        else:
            # Save changes to the NGOProfile table
            profile.ngo_name = ngo_name
            profile.address = address
            profile.city = city

            profile.save()

            messages.success(
                request,
                "NGO profile updated successfully."
            )

            return redirect("update_profile")

    return render(
        request,
        "ngo/update_profile.html",
        {
            "profile": profile
        }
    )