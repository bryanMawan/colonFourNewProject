from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, OrganizerProfile, OrganizerVerificationRequest, Dancer, Battle, Event, Tip
from PIL import Image
import io


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
            'styles', 'level', 'poster', 'video', 'judges', 'type', 'host', 'is_7tosmoke',
        ]

    def clean(self):
        cleaned_data = super().clean()

        # Calculate size of the poster image
        poster = self.files.get('poster')
        if poster:
            size_of_poster = self.calculate_image_size(poster)
            print(f"Size of poster image: {size_of_poster} bytes")

        # Calculate size of each carousel image
        carousel_images = self.files.getlist('info_pics_carousel')
        total_carousel_size = 0
        for image in carousel_images:
            size = self.calculate_image_size(image)
            total_carousel_size += size
            print(f"Size of carousel image: {size} bytes")

        print(f"Total size of carousel images: {total_carousel_size} bytes")

        return cleaned_data

    def calculate_image_size(self, image_field):
        """Helper function to calculate the size of an image in bytes."""
        if not image_field:
            return 0
        # Using Pillow to calculate size
        try:
            image = Image.open(image_field)
            with io.BytesIO() as img_byte_arr:
                image.save(img_byte_arr, format=image.format)
                size = img_byte_arr.tell()
            return size
        except Exception as e:
            print(f"Error calculating image size: {e}")
            return 0

    def save(self, commit=True):
        return super().save(commit=commit)
    

class TipForm(forms.ModelForm):
    class Meta:
        model = Tip
        exclude = ['video']  # Exclude the video field from the for
