from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

class FutureDateValidationMixin(forms.ModelForm):
    def clean_date(self):
        date = self.cleaned_data['date']
        tomorrow = timezone.now() + timezone.timedelta(days=1)
        if date < tomorrow:
            raise ValidationError("The date cannot be earlier than tomorrow.")
        # Debug print to show the cleaned date
        print(f"Cleaned event date: {date}")
        return date

    def clean(self):
        cleaned_data = super().clean()
        # Debug print to show all cleaned data
        print(f"{self.__class__.__name__} cleaned data:")
        for field, value in cleaned_data.items():
            print(f"{field}: {value}")
        return cleaned_data
