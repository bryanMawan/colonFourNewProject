# yourapp/views.py
import logging
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods
from django.views.generic import TemplateView, DetailView, CreateView, ListView

from .forms import (
    OrganizerRegistrationForm,
    OrganizerVerificationRequestForm,
    DancerForm,
    BattleForm,
    TipForm,
)
from .models import OrganizerProfile, Dancer, Battle, Event, Tip, EventImage
from .selectors import (
    get_all_dancers,
    get_sorted_events,
    get_unique_styles,
    get_unique_event_types,
    get_unique_levels,
    get_dancers_info
)
from .servicesFolder.services import (
    update_organizer_profile,
    dancer_success_msg,
    get_all_styles,
    set_battle_organizer,
    update_event_location_point,
    geo_db,
    generate_totp_code,
    send_code,
    verify_totp_code,
    hash_telephone_number,
    sanitize_instagram_account
)




logger = logging.getLogger(__name__)


class HomePageView(TemplateView):
    template_name = 'home.html'


@require_GET
def fetch_suboptions(request):
    option = request.GET.get('option')

    suboptions = {
        'styles': get_unique_styles(),
        'event-type': get_unique_event_types(),
        'format': ['Online', 'Offline'],
        'level': get_unique_levels()
    }

    data = suboptions.get(option, [])
    return JsonResponse({'suboptions': data})


class SearchHomePage(ListView):
    model = Event
    template_name = 'home.html'
    context_object_name = 'events'

    def get_search_query(self):
        search_query = self.request.GET.get('search-box', 'Paris, France')
        logger.debug(f"Search query: {search_query}")
        return search_query

    def get_utc_date_str(self):
        utc_date_str = self.request.GET.get('utc-date', now().isoformat())
        try:
            # Validate UTC date format
            datetime.strptime(utc_date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            logger.warning(f"Invalid UTC date format: {utc_date_str}. Using current time instead.")
            utc_date_str = now().isoformat()
        logger.debug(f"UTC date string: {utc_date_str}")
        return utc_date_str

    def get_filters(self):
        raw_filters = self.request.GET.dict()
        logger.debug(f"Raw filter parameters: {raw_filters}")

        filters = {}
        for key, value in raw_filters.items():
            if key in ['search-box', 'utc-date']:
                continue  # Skip these special keys
            if ',' in value:
                filters[key] = value.split(", ")
            else:
                filters[key] = [value]
        logger.debug(f"Parsed filters: {filters}")
        return filters

    def get_order_by(self):
        raw_filters = self.request.GET.dict()
        user_friendly_order = raw_filters.get('order-by', 'Soonest')
        
        order_mapping = {
            'Soonest ↑': 'soonest-a',
            'Soonest ↓': 'soonest-d',
            'Closest ↑': 'distance-a',
            'Closest ↓': 'distance-d',
            'Popular ↑': 'goers-a',
            'Popular ↓': 'goers-d'
        }

        order_by = order_mapping.get(user_friendly_order, 'distance-d')  # Default to 'soonest-a'
        logger.debug(f"Order by parameter: {order_by}")
        return order_by

    def get_queryset(self):
        try:
            search_query = self.get_search_query()
            utc_date_str = self.get_utc_date_str()
            filters = self.get_filters()
            order_by = self.get_order_by()

            events = get_sorted_events(search_query=search_query, utc_date_str=utc_date_str, filters=filters, order_by=order_by)

            if not events:
                logger.warning("No events found matching the criteria.")
            
            logger.debug(f"Final queryset count: {len(events)}")
            return events
        except Exception as e:
            logger.error(f"Error fetching queryset: {e}")
            return Event.objects.none()  # Return an empty queryset in case of error

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_maps_api_key'] = settings.GOOGLE_MAPS_API_KEY
        logger.debug(f"Context data: {context}")
        return context

    
def register(request):
    if request.method == 'POST':
        form = OrganizerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            gdpr_consented = form.cleaned_data.get('gdpr_consented', False)
            instagram_account = request.POST.get('instagram_account')

            logger.debug(f"Instagram account: {instagram_account}")
            update_organizer_profile(user, gdpr_consented, instagram_account)
            login(request, user)
            messages.success(request, f'Welcome {user.get_full_name()}!')
            return redirect('home')
        else:
            logger.warning(f"Invalid registration attempt: {form.errors}")
    else:
        form = OrganizerRegistrationForm()
        logger.debug("Rendering registration form")
        
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
        print(organizer.instagram_account)
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
        

        # Debug print to check styles before saving
        print(f"Form styles before save: {battle.styles}")

        update_event_location_point(battle, geo_db)  # Update the location point
        battle.save()  # Now save the battle to the database
        # Handle many-to-many relationships
        form.save_m2m()

        # Debug print to check if the post dictionary
        print(f"POST dictionary: {self.request.POST}")

        # Handle info_pics_carousel
        info_pics_files = self.request.FILES.getlist('info_pics_carousel')

        for image_file in info_pics_files:
            # Check file type before saving
            if not image_file.name.endswith(('.png', '.jpg', '.jpeg')):
                # Log the error
                logger.error(f"Invalid file type uploaded: {image_file.name}")
                # Raise a validation error and send an error message to the template
                form.add_error('info_pics_carousel', ValidationError("Invalid file type. Please upload only PNG, JPG, or JPEG files."))
                return self.form_invalid(form)

            EventImage.objects.create(event=battle, image=image_file)

        # Debug print to check images after saving
        print(f"Battle info_pics_carousel count: {battle.info_pics_carousel.count()}")

        # Set the current user as the host of the battle
        response = super().form_valid(form)

        # Log the creation of the battle. Move the detailed logging logic to services if needed.
        user_name = self.request.user.get_full_name()
        battle_name = form.cleaned_data['name']
        logger.info(f'User "{user_name}" created a battle: "{battle_name}"')

        # Show success message
        messages.success(self.request, f'Battle "{battle_name}" has been successfully created.')

        return response
    

@csrf_exempt  # Note: Better to use csrf token in AJAX request for security
@require_http_methods(["POST"])
def send_code_view(request):
    # Dummy implementation for sending the code
    # Extract phone number from POST data
    phone_number = request.POST.get('phoneNumber', '')
    
    # Here you would call your method to send the actual code to the phone number
    code = generate_totp_code(phone_number)

    logger.debug(f'code "{code}" for number; "{phone_number}"')

    # sendCode(totp_code, 'SMS', phone_number)
    send_code(code, phone_number)
    # For now, we just simulate a successful operation
    return JsonResponse({"message": "Code sent successfully", "success": True})


@csrf_exempt
@require_http_methods(["POST"])
def verify_code_view(request):
    phone_number = request.POST.get('phoneNumber', '')
    submitted_code = request.POST.get('smsCode', '')
    going_toggle = request.POST.get('goingToggle') == 'true'
    print(going_toggle)

    current_event_id = request.POST.get('eventId') 
    print("current_event_id: " + current_event_id)

    if verify_totp_code(submitted_code, phone_number):
        process_msg = ""
        event = get_object_or_404(Event, id=current_event_id)
        hashed_phone_number = hash_telephone_number(phone_number)

        if going_toggle:
            event.remove_goer(hashed_phone_number)
            process_msg = "removed"
            logger.info(f'"{phone_number}" hashed and {process_msg} to "{event.name}" event')

        else:
            event.add_goer(hashed_phone_number)
            process_msg = "added"
            logger.info(f'"{phone_number}" hashed and {process_msg} to "{event.name}" event')


        # Logic for when the toggle is off
        return JsonResponse({"message": f"You have been {process_msg} successfully", "valid": True})
    else:
        return JsonResponse({"message": "Invalid code or code expired", "valid": False}, status=400)
    

class CreateTipView(CreateView):
    model = Tip
    form_class = TipForm
    template_name = 'create_tip.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        tip_name = form.instance.name  # Get the name of the created tip
        logger.info(f"A tip has been created: {tip_name}")
        return response
    

@require_GET
def get_event_details(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    images = [{'url': image.image.url} for image in event.info_pics_carousel.all()]

    # Retrieve dancer information related to the event
    dancers_info = get_dancers_info(event)

    # Fetch event styles
    event_styles = event.get_styles()

    data = {
        'name': event.name,
        'description': event.description,
        'images': images,
        'organizer_instagram': event.organizer.instagram_account,
        'dancers': dancers_info,  # Include the retrieved dancers info
        'styles': event_styles  # Include the event styles
    }

    logger.debug(f"Event details for {event.name}: {data}")

    return JsonResponse(data)

def delete_past_events_view(request):
    # Only allow GET requests
    if request.method == 'GET':
        # Logic to delete past events
        deleted_count, _ = Event.objects.filter(date__lt=timezone.now()).delete()
        logger.debug(f"{deleted_count} past events have been deleted.")
        return HttpResponse(f'{deleted_count} past events have been successfully deleted.')
    else:
        return HttpResponse(status=405)  # Method Not Allowed
