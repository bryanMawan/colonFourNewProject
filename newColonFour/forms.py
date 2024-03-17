from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, OrganizerProfile, OrganizerVerificationRequest, Dancer, Battle, Event

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


class DancerForm(forms.ModelForm):
    dancer_has_consented = forms.BooleanField(
        required=True,  # Set to True if you want the field to be required
    )

    class Meta:
        model = Dancer
        fields = ['name', 'country', 'picture', 'styles', 'dancer_has_consented']

class BattleForm(forms.ModelForm):
    class Meta:
        model = Battle
        fields = [
            'name', 'date', 'location', 'description', 'start_time', 'end_time',
            'styles', 'level', 'poster', 'video', 'judges', 'type', 'host', 'is_7tosmoke'
        ]

    def __init__(self, *args, **kwargs):
        super(BattleForm, self).__init__(*args, **kwargs)
        # Customize form widgets or add additional validation if needed

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        # Add custom validation logic for time fields if needed

        return cleaned_data
