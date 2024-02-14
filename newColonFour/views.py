# yourapp/views.py
from django.views.generic import TemplateView, DetailView, CreateView
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import OrganizerRegistrationForm, OrganizerVerificationRequestForm, DancerForm, BattleForm
from .models import OrganizerProfile, Dancer, Battle
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages 
from django.contrib.auth.views import LoginView
from .services import update_organizer_profile, dancer_success_msg, get_all_styles, set_battle_organizer
from .selectors import get_all_dancers
from django.urls import reverse_lazy
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404


import logging

logger = logging.getLogger(__name__)



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
    
    def form_invalid(self, form):
        # Add a generic error message
        messages.error(self.request, 'Login failed. Please check your credentials and try again.')
        # Reload the login page
        return super().form_invalid(form)


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

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Get the organizer from the context
        organizer = context['organizer']
        # Fetch the organizer's events
        events = organizer.organized_events.all()
        # Log the events for debugging
        logger.info(f'Organizer {organizer} events: {list(events)}')
        # Optionally, add the events to the context (if needed)
        context['events'] = events
        return context


# @method_decorator(ratelimit(key='user', rate='15/s', method='POST', block=True), name='dispatch')
class DancerCreateView(LoginRequiredMixin, CreateView):
    model = Dancer
    form_class = DancerForm
    template_name = 'dancer/createDancer.html'
    success_url = reverse_lazy('create_dancer')
    login_url = '/login/'  # Redirect to the login page if the user is not authenticated

    def form_valid(self, form):
        response = super().form_valid(form)
        # from here (move to services)
        user_name = self.request.user.get_full_name()
        dancer_name = form.cleaned_data['name']
        logger.debug(f'User "{user_name.title()}" created a dancer: "{dancer_name.title()}"')
        # to here (move to services)
        messages.success(self.request, f'"{self.object.name}"' + dancer_success_msg)
        return response
    
    def get_context_data(self, **kwargs):
        context = super(DancerCreateView, self).get_context_data(**kwargs)
        context['all_dancers'] = get_all_dancers()  # Use the selector to add all dancers to the context
        return context
    
    def dispatch(self, request, *args, **kwargs):
        if getattr(request, 'limited', False):
            logger.warning(f"Rate limit exceeded for user {request.user.username}")
        return super(DancerCreateView, self).dispatch(request, *args, **kwargs)
    

class BattleCreate(LoginRequiredMixin, CreateView):
    model = Battle
    form_class = BattleForm
    template_name = 'event/battle.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super(BattleCreate, self).get_context_data(**kwargs)
        context['all_dancers'] = get_all_dancers()  # Use the selector to add all dancers to the context
        context['all_styles'] = get_all_styles()  # Use the service to get all styles

        return context
    
    def get_success_url(self):
        """
        Override the get_success_url method to redirect to the organizer's profile page.
        """
        organizer_profile = get_object_or_404(OrganizerProfile, user=self.request.user)
        # Then, construct the URL using the 'organizer-profile-detail' view and the organizer's slug.
        return reverse_lazy('organizer-profile-detail', kwargs={'slug': organizer_profile.slug})

    def form_valid(self, form):
        battle = form.save(commit=False)  # Save the form instance but don't commit to db yet
        battle = set_battle_organizer(battle, self.request.user)  # Update battle's organizer
        battle.save()  # Now save the battle to the database
        # Set the current user as the host of the battle
        response = super().form_valid(form)

        
        # Log the creation of the battle. Move the detailed logging logic to services if needed.
        user_name = self.request.user.get_full_name()
        battle_name = form.cleaned_data['name']
        logger.info(f'User "{user_name}" created a battle: "{battle_name}"')
        
        # Show success message
        messages.success(self.request, f'Battle "{battle_name}" has been successfully created.')
        
        return response


