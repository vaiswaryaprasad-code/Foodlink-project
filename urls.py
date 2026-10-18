from django.urls import path
from . import views


urlpatterns = [

    path(
        "dashboard/",
        views.dashboard,
        name="ngo_dashboard"
    ),

    path(
        "available/",
        views.available_food,
        name="available_food"
    ),

    path(
        "claim/<int:id>/",
        views.claim_food,
        name="claim_food"
    ),

    path(
        "history/",
        views.claim_history,
        name="claim_history"
    ),

    path(
        "pickup/<int:id>/",
        views.pickup_food,
        name="pickup_food"
    ),

    path(
        "deliver/<int:id>/",
        views.deliver_food,
        name="deliver_food"
    ),

    path(
        "update-status/<int:id>/<str:status>/",
        views.update_status,
        name="update_status"
    ),
    
    path(
    "update-profile/",
    views.update_profile,
    name="update_profile"
),
]