# yourapp/views.py
from django.views.generic import TemplateView, DetailView
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import OrganizerRegistrationForm, OrganizerVerificationRequestForm
from .models import OrganizerProfile
from django.contrib.auth.mixins import LoginRequiredMixin



class HomePageView(TemplateView):
    template_name = 'home.html'

def register(request):
    if request.method == 'POST':
        form = OrganizerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log in the user
            login(request, user)

            # Redirect to the home page after successful registration and login
            return redirect('home')

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

class OrganizerProfileDetailView(LoginRequiredMixin, DetailView):
    model = OrganizerProfile
    template_name = 'organizer_profile_detail.html'
    context_object_name = 'organizer'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    login_url = '/login/'  # Update this with your login route if it's different
