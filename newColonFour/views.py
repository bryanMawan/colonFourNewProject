# yourapp/views.py
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import OrganizerRegistrationForm, OrganizerVerificationRequestForm
from .models import OrganizerProfile


class HomePageView(TemplateView):
    template_name = 'home.html'

def register(request):
    if request.method == 'POST':
        form = OrganizerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log in the user
            login(request, user)

            # Check if the user's organizer profile is verified
            organizer_profile = OrganizerProfile.objects.get(user=user)
            if organizer_profile.is_verified_status:
                return redirect('home')  # Redirect to the home page
            else:
                return redirect('org_verification')  # Redirect to the orgVerification page

    else:
        form = OrganizerRegistrationForm()

    return render(request, 'registration.html', {'form': form})

def org_verification(request):
    if request.method == 'POST':
        form = OrganizerVerificationRequestForm(request.POST)
        if form.is_valid():
            verification_request = form.save(commit=False)
            organizer_profile = OrganizerProfile.objects.get(user=request.user)
            verification_request.organizer_profile = organizer_profile
            verification_request.save()
            # Redirect to a confirmation page or the home page
            return redirect('home')
    else:
        form = OrganizerVerificationRequestForm()

    return render(request, 'user_verification.html', {'form': form})
