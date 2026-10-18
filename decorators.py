from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


# =========================================================
# ADMIN REQUIRED
# =========================================================

def admin_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if not request.user.is_superuser:

            messages.error(
                request,
                "You are not authorized to access this page."
            )

            return redirect("home")

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper


# =========================================================
# DONOR REQUIRED
# =========================================================

def donor_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        # -----------------------------------------------
        # USER MUST BE LOGGED IN
        # -----------------------------------------------

        if not request.user.is_authenticated:

            return redirect("login")

        # -----------------------------------------------
        # CHECK DONOR ROLE
        # -----------------------------------------------

        if request.user.user_type != "DONOR":

            messages.error(
                request,
                "Only donors can access this page."
            )

            return redirect("home")

        # -----------------------------------------------
        # CHECK ADMIN APPROVAL
        # -----------------------------------------------

        if not request.user.is_approved:

            messages.warning(
                request,
                "Your account is waiting for admin verification."
            )

            return redirect("login")

        # -----------------------------------------------
        # CHECK VERIFICATION STATUS
        # -----------------------------------------------

        if request.user.verification_status != "VERIFIED":

            # -------------------------------------------
            # REJECTED
            # -------------------------------------------

            if request.user.verification_status == "REJECTED":

                if request.user.verification_note:

                    messages.error(
                        request,
                        f"Your verification was rejected. "
                        f"Reason: {request.user.verification_note}"
                    )

                else:

                    messages.error(
                        request,
                        "Your verification was rejected by the admin."
                    )

            # -------------------------------------------
            # PENDING
            # -------------------------------------------

            else:

                messages.warning(
                    request,
                    "Your account is waiting for admin verification."
                )

            return redirect("login")

        # -----------------------------------------------
        # VERIFIED DONOR
        # -----------------------------------------------

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper


# =========================================================
# NGO REQUIRED
# =========================================================

def ngo_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        # -----------------------------------------------
        # USER MUST BE LOGGED IN
        # -----------------------------------------------

        if not request.user.is_authenticated:

            return redirect("login")

        # -----------------------------------------------
        # CHECK NGO ROLE
        # -----------------------------------------------

        if request.user.user_type != "NGO":

            messages.error(
                request,
                "Only NGOs can access this page."
            )

            return redirect("home")

        # -----------------------------------------------
        # CHECK ADMIN APPROVAL
        # -----------------------------------------------

        if not request.user.is_approved:

            messages.warning(
                request,
                "Your account is waiting for admin verification."
            )

            return redirect("login")

        # -----------------------------------------------
        # CHECK VERIFICATION STATUS
        # -----------------------------------------------

        if request.user.verification_status != "VERIFIED":

            # -------------------------------------------
            # REJECTED
            # -------------------------------------------

            if request.user.verification_status == "REJECTED":

                if request.user.verification_note:

                    messages.error(
                        request,
                        f"Your verification was rejected. "
                        f"Reason: {request.user.verification_note}"
                    )

                else:

                    messages.error(
                        request,
                        "Your verification was rejected by the admin."
                    )

            # -------------------------------------------
            # PENDING
            # -------------------------------------------

            else:

                messages.warning(
                    request,
                    "Your account is waiting for admin verification."
                )

            return redirect("login")

        # -----------------------------------------------
        # VERIFIED NGO
        # -----------------------------------------------

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper


# =========================================================
# VERIFIED USER REQUIRED
# =========================================================

def verified_user_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        # -----------------------------------------------
        # USER MUST BE LOGGED IN
        # -----------------------------------------------

        if not request.user.is_authenticated:

            return redirect("login")

        # -----------------------------------------------
        # ADMIN CAN ACCESS
        # -----------------------------------------------

        if request.user.is_superuser:

            return view_func(
                request,
                *args,
                **kwargs
            )

        # -----------------------------------------------
        # CHECK APPROVAL
        # -----------------------------------------------

        if not request.user.is_approved:

            messages.warning(
                request,
                "Your account is waiting for admin verification."
            )

            return redirect("login")

        # -----------------------------------------------
        # CHECK VERIFICATION
        # -----------------------------------------------

        if request.user.verification_status != "VERIFIED":

            if request.user.verification_status == "REJECTED":

                if request.user.verification_note:

                    messages.error(
                        request,
                        f"Your verification was rejected. "
                        f"Reason: {request.user.verification_note}"
                    )

                else:

                    messages.error(
                        request,
                        "Your verification was rejected by the admin."
                    )

            else:

                messages.warning(
                    request,
                    "Your account is waiting for admin verification."
                )

            return redirect("login")

        # -----------------------------------------------
        # VERIFIED USER
        # -----------------------------------------------

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper