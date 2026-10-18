from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import FoodDonation
import re
from django.utils import timezone


class FoodDonationForm(forms.ModelForm):

    class Meta:
        model = FoodDonation

        fields = [
            'food_name',
            'food_type',
            'quantity',
            'prepared_time',
            'expiry_time',
            'pickup_address',
            'city',
            'image',
        ]

        widgets = {
            'food_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter food name'
                }
            ),

            'food_type': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),

            'quantity': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter quantity',
                    'min': '1'
                }
            ),

            'prepared_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                },
                format='%Y-%m-%dT%H:%M'
            ),

            'expiry_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                },
                format='%Y-%m-%dT%H:%M'
            ),

            'pickup_address': forms.Textarea(
                attrs={
                    'rows': 3,
                    'class': 'form-control',
                    'placeholder': 'Enter the food pickup location/address'
                }
            ),

            'city': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter city'
                }
            ),

            'image': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                    'accept': 'image/*'
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        prepared_time = cleaned_data.get('prepared_time')
        expiry_time = cleaned_data.get('expiry_time')
        now = timezone.now()

        # 1. Preparation time cannot be in the future
        if prepared_time and prepared_time > now:
            self.add_error(
                'prepared_time',
                'Preparation date and time cannot be in the future.'
            )

        # 2. Expiry time must be later than preparation time
        if prepared_time and expiry_time and expiry_time <= prepared_time:
            self.add_error(
                'expiry_time',
                'Expiry date and time must be later than preparation time.'
            )

        # 3. Expiry time must be in the future
        if expiry_time and expiry_time <= now:
            self.add_error(
                'expiry_time',
                'Expiry date and time must be in the future.'
            )

        # 4. Quantity must be positive
        quantity = cleaned_data.get('quantity')

        if quantity is not None and quantity <= 0:
            self.add_error(
                'quantity',
                'Quantity must be greater than zero.'
            )

        return cleaned_data

# ==========================================
# FOOD NAME VALIDATION
# ==========================================

def clean_food_name(self):

    food_name = self.cleaned_data.get('food_name')

    if not food_name:
        raise ValidationError(
            "Food name is required."
        )

    food_name = food_name.strip()

    if len(food_name) < 2:
        raise ValidationError(
            "Food name must contain at least 2 characters."
        )

    if len(food_name) > 100:
        raise ValidationError(
            "Food name cannot exceed 100 characters."
        )

    if not re.match(
        r"^[A-Za-z0-9 .,&'()/-]+$",
        food_name
    ):
        raise ValidationError(
            "Food name contains invalid characters."
        )

    return food_name


# ==========================================
# FOOD TYPE VALIDATION
# ==========================================

def clean_food_type(self):

    food_type = self.cleaned_data.get('food_type')

    if not food_type:
        raise ValidationError(
            "Food type is required."
        )

    food_type = food_type.strip()

    if len(food_type) < 2:
        raise ValidationError(
            "Food type must contain at least 2 characters."
        )

    if not re.match(
        r"^[A-Za-z ]+$",
        food_type
    ):
        raise ValidationError(
            "Food type can contain only letters and spaces."
        )

    return food_type


# ==========================================
# QUANTITY VALIDATION
# ==========================================

def clean_quantity(self):

    quantity = self.cleaned_data.get('quantity')

    if quantity is None:
        raise ValidationError(
            "Quantity is required."
        )

    if quantity <= 0:
        raise ValidationError(
            "Quantity must be greater than 0."
        )

    return quantity


# ==========================================
# PICKUP ADDRESS VALIDATION
# ==========================================

def clean_pickup_address(self):

    address = self.cleaned_data.get('pickup_address')

    if not address:
        raise ValidationError(
            "Pickup address is required."
        )

    address = address.strip()

    if len(address) < 5:
        raise ValidationError(
            "Please enter a complete pickup address."
        )

    if len(address) > 500:
        raise ValidationError(
            "Pickup address cannot exceed 500 characters."
        )

    return address


# ==========================================
# CITY VALIDATION
# ==========================================

def clean_city(self):

    city = self.cleaned_data.get('city')

    if not city:
        raise ValidationError(
            "City is required."
        )

    city = city.strip()

    if len(city) < 2:
        raise ValidationError(
            "City name must contain at least 2 characters."
        )

    if len(city) > 100:
        raise ValidationError(
            "City name cannot exceed 100 characters."
        )

    if not re.match(
        r"^[A-Za-z ]+$",
        city
    ):
        raise ValidationError(
            "City can contain only letters and spaces."
        )

    return city


# ==========================================
# PREPARED TIME VALIDATION
# ==========================================

def clean_prepared_time(self):

    prepared_time = self.cleaned_data.get(
        'prepared_time'
    )

    if not prepared_time:
        raise ValidationError(
            "Prepared time is required."
        )

    if prepared_time > timezone.now():
        raise ValidationError(
            "Prepared time cannot be in the future."
        )

    return prepared_time


# ==========================================
# EXPIRY TIME VALIDATION
# ==========================================

def clean_expiry_time(self):

    expiry_time = self.cleaned_data.get(
        'expiry_time'
    )

    if not expiry_time:
        raise ValidationError(
            "Expiry time is required."
        )

    return expiry_time


# ==========================================
# IMAGE VALIDATION
# ==========================================

def clean_image(self):

    image = self.cleaned_data.get('image')

    # Image is optional
    if not image:
        return image

    # Maximum size = 5 MB
    max_size = 5 * 1024 * 1024

    if image.size > max_size:
        raise ValidationError(
            "Image size must not exceed 5 MB."
        )

    allowed_extensions = [
        '.jpg',
        '.jpeg',
        '.png',
        '.webp'
    ]

    file_name = image.name.lower()

    if not any(
        file_name.endswith(ext)
        for ext in allowed_extensions
    ):
        raise ValidationError(
            "Only JPG, JPEG, PNG and WEBP images are allowed."
        )

    return image


# ==========================================
# FINAL FORM VALIDATION
# ==========================================

def clean(self):

    cleaned_data = super().clean()

    prepared_time = cleaned_data.get(
        'prepared_time'
    )

    expiry_time = cleaned_data.get(
        'expiry_time'
    )

    # --------------------------------------
    # Expiry must be after preparation
    # --------------------------------------

    if prepared_time and expiry_time:

        if expiry_time <= prepared_time:

            self.add_error(
                'expiry_time',
                "Expiry time must be later than prepared time."
            )

    return cleaned_data
