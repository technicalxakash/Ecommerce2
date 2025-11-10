from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Address

# ✅ Profile Update Form
class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(max_length=100)

    class Meta:
        model = UserProfile
        fields = ['phone', 'profile_image']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email

# ✅ Address Form
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'phone', 'address_line', 'city', 'state', 'postal_code', 'is_default']
