from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, OrganizerProfile, OrganizerVerificationRequest

class OrganizerRegistrationForm(UserCreationForm):
    gdpr_consented = forms.BooleanField(
        required=True,
        label="I have read and agree to the Terms and Conditions"
    )

    class Meta:
        model = CustomUser
        fields = ("email", "name", "password1", "password2", "gdpr_consented")

    def save(self, commit=True):
        return super().save(commit=commit)

    
class OrganizerVerificationRequestForm(forms.ModelForm):
    class Meta:
        model = OrganizerVerificationRequest
        fields = ['url']
