# yourapp/views.py
from django.views.generic import TemplateView, DetailView
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import OrganizerRegistrationForm, OrganizerVerificationRequestForm
from .models import OrganizerProfile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages 
from django.contrib.auth.views import LoginView
from .services import update_organizer_profile





class HomePageView(TemplateView):
    template_name = 'home.html'

def register(request):
    if request.method == 'POST':
        form = OrganizerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            gdpr_consented = form.cleaned_data.get('gdpr_consented', False)
            # Call the service function
            update_organizer_profile(user, gdpr_consented)
            # Log in the user
            login(request, user)

            # Add a success message
            messages.success(request, f'Welcome {user.get_full_name()}!')

            # Redirect to the home page after successful registration and login
            return redirect('home')

    else:
        form = OrganizerRegistrationForm()

    return render(request, 'registration.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'login.html'

    def form_valid(self, form):
        # Perform the login
        login(self.request, form.get_user())

        # Add a success message
        messages.success(self.request, f'Welcome back {form.get_user().get_full_name()}!')

        # Redirect to the home page
        return redirect('home')

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
