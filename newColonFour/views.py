# yourapp/views.py
import logging
from datetime import datetime
from django.template.loader import render_to_string


from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods
from django.views.generic import TemplateView, DetailView, CreateView, ListView
from django.views import View
from django.core.cache import cache
import time


from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import EventSerializer
from django.core.paginator import Paginator

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
)
from .cache_utils import (
    set_cache_with_prefix,
    get_cache_with_prefix,
    generate_cache_key
)

import hashlib

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
        'level': get_unique_levels(),
        'dancers': Dancer.get_all_dancer_names()  # Add dancer names here

    }
    data = suboptions.get(option, [])
    return JsonResponse({'suboptions': data})

def fetch_updated_options(request):
    # Query for the latest judges and hosts
    judges = Dancer.objects.filter(battle_judges__isnull=False).distinct().values('id', 'name')
    hosts = Dancer.objects.filter(battle_hosts__isnull=False).distinct().values('id', 'name')

    # Prepare the data in a dictionary format
    data = {
        'judges': list(judges),
        'hosts': list(hosts)
    }

    # Return the data as JSON response
    return JsonResponse(data)

def get_partial_content(request):
    form = BattleForm()
    context = {'form': form}
    html = render_to_string('partial_content.html', context, request=request)
    return JsonResponse({'html': html})

class SearchHomePage(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_maps_api_key'] = settings.GOOGLE_MAPS_API_KEY
        return context


class EventPagination(PageNumberPagination):
    page_size = 4  # Set the number of events per page


class EventAjaxView(APIView):
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('search-box', 'Paris, France')
        print(f"Debug - search_query: {search_query}")

        if search_query == "":
            search_query = 'Paris, France'

        raw_filters = request.GET.dict()
        logger.debug(f"Raw filters received: {raw_filters}")

        order_by = raw_filters.get('order-by', 'Closest ↑')
        filters = {k: v.split(", ") if ',' in v else [v] for k, v in raw_filters.items()
                   if k not in ['search-box', 'order-by', 'offset', 'limit'  ]}

        order_mapping = {
            'Soonest ↑': 'soonest-a',
            'Soonest ↓': 'soonest-d',
            'Closest ↑': 'distance-a',
            'Closest ↓': 'distance-d',
            'Popular ↑': 'goers-a',
            'Popular ↓': 'goers-d'
        }
        order_by = order_mapping.get(order_by, 'soonest-a')

        # Extract pagination parameters
        try:
            offset = int(request.GET.get('offset', 0))
            limit = int(request.GET.get('limit', 4))
        except ValueError:
            return Response({'error': 'Invalid offset or limit parameters'}, status=400)

        # Generate a unique cache key based on search query, filters, and order_by
        
        cache_key = generate_cache_key(search_query, order_by, filters)
        events = get_cache_with_prefix("event_load", cache_key)


        if not events:
            try:
                # Fetch and sort events based on the search query, filters, and order_by
                events = get_sorted_events(
                    search_query=search_query,
                    filters=filters,
                    order_by=order_by
                )
                set_cache_with_prefix("event_load", cache_key, events, timeout=60*1)
                
            except Exception as e:
                logger.error(f"Error fetching events: {e}")
                return Response({'error': 'Unable to fetch events'}, status=500)

        # Apply Django's built-in pagination
        paginator = Paginator(events, limit)  # limit is the number of events per page
        page_number = (offset // limit) + 1  # Page number is offset divided by limit plus 1

        if page_number > paginator.num_pages:
            # If the page number exceeds the number of available pages, return an empty response
            return Response({'results': [], 'count': paginator.count, 'next': None, 'previous': None})

        page = paginator.get_page(page_number)

        # Serialize only the events on the current page
        serializer = EventSerializer(page.object_list, many=True)

        print("[DEBUG] Serialized events data:")
        print(serializer.data)

        # Return paginated response
        response_data = {
            'results': serializer.data,
            'count': paginator.count,  # Total count of events
            'next': page.next_page_number() if page.has_next() else None,
            'previous': page.previous_page_number() if page.has_previous() else None,
        }
        return Response(response_data)



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
        messages.success(
            self.request, f'Welcome back {form.get_user().get_full_name()}!')
        # Redirect to the home page
        return redirect('home')

    def form_invalid(self, form):
        # Add a generic error message
        messages.error(
            self.request, 'Login failed. Please check your credentials and try again.')
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


# Use this if you can't use CSRF middleware. Otherwise, remove this decorator.
@csrf_exempt
def create_dancer(request):
    if request.method == 'POST':
        form = DancerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            errors = [f"{field}: {error}" for field,
                      error_list in form.errors.items() for error in error_list]
            return JsonResponse({'success': False, 'errors': errors})
    return JsonResponse({'success': False, 'errors': ['Invalid request method.']})


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
        logger.debug(
            f'User "{user_name.title()}" created a dancer: "{dancer_name.title()}"')
        # to here (move to services)
        messages.success(
            self.request, f'"{self.object.name}"' + dancer_success_msg)
        return response

    def get_context_data(self, **kwargs):
        context = super(DancerCreateView, self).get_context_data(**kwargs)
        # Use the selector to add all dancers to the context
        context['all_dancers'] = get_all_dancers()
        return context

    def dispatch(self, request, *args, **kwargs):
        if getattr(request, 'limited', False):
            logger.warning(
                f"Rate limit exceeded for user {request.user.username}")
        return super(DancerCreateView, self).dispatch(request, *args, **kwargs)


class BattleCreate(LoginRequiredMixin, CreateView):
    model = Battle
    form_class = BattleForm
    template_name = 'event/battle.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super(BattleCreate, self).get_context_data(**kwargs)
        # Use the selector to add all dancers to the context
        context['all_dancers'] = get_all_dancers()
        # Use the service to get all styles
        context['all_styles'] = get_all_styles()
        context['dancer_form'] = DancerForm()  # Add dancer form to the context
        context['google_maps_api_key'] = settings.GOOGLE_MAPS_API_KEY

        return context

    def get_success_url(self):
        """
        Override the get_success_url method to redirect to the organizer's profile page.
        """
        organizer_profile = get_object_or_404(
            OrganizerProfile, user=self.request.user)
        # Then, construct the URL using the 'organizer-profile-detail' view and the organizer's slug.
        return reverse_lazy('organizer-profile-detail', kwargs={'slug': organizer_profile.slug})
    
    def clear_event_cache(self):
        client_location = "Paris, France"
        default_load_key_string = f"event_ajax_view_{client_location}_" + "{'utc-date': [''], 'offset': ['0'], 'limit': ['4']}_distance-a"
        hashlib.md5(default_load_key_string.encode()).hexdigest()
        logger.info(f"Cache cleared for keys with prefix '{default_load_key_string}'")

    def form_valid(self, form):
        start_time = time.time()

        # Create a new Battle instance without saving to the database
        battle = form.save(commit=False)
        
        # Modify the battle instance as needed
        battle = set_battle_organizer(battle, self.request.user)

        # Debug print to check selected styles
        styles = form.cleaned_data.get('styles', [])
        logger.debug(f"Selected styles: {styles}")
        
        # Debug print to check styles before saving
        logger.debug(f"Form styles before save: {battle.styles}")
        
        # Update the location point
        update_event_location_point(battle, geo_db)

        self.handle_info_pics_carousel(battle)
        logger.debug(f"Battle info_pics_carousel count: {battle.info_pics_carousel.count()}")
        
        # Assign the modified battle instance to self.object
        self.object = battle
        logger.debug(f"Battle object before saving: {battle.__dict__}")

        # Call super().form_valid(form) to save the instance and handle redirection
        response = super().form_valid(form)
        
        user_name = self.request.user.get_full_name()
        battle_name = form.cleaned_data['name']
        logger.info(f'User "{user_name}" created a battle: "{battle_name}"')
        messages.success(self.request, f'Battle "{battle_name}" has been successfully created.')
        
        self.clear_event_cache()
        end_time = time.time()
        execution_time = end_time - start_time
        logger.warning(f'Execution time for BattleCreate: {execution_time} seconds')

        return response
    
    def handle_info_pics_carousel(self, battle):
        info_pics_files = self.request.FILES.getlist('info_pics_carousel')
        for image_file in info_pics_files:
            if not image_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                logger.error(f"Invalid file type uploaded: {image_file.name}")
                raise ValidationError("Invalid file type. Please upload only PNG, JPG, or JPEG files.")
            EventImage.objects.create(event=battle, image=image_file)
            


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
            logger.info(
                f'"{phone_number}" hashed and {process_msg} to "{event.name}" event')

        else:
            event.add_goer(hashed_phone_number)
            process_msg = "added"
            logger.info(
                f'"{phone_number}" hashed and {process_msg} to "{event.name}" event')

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

    images = [{'url': image.image.url}
              for image in event.info_pics_carousel.all()]

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

    logger.debug(f"\nEvent details print out format for {event.name}: {data}\n")

    return JsonResponse(data)


def delete_past_events_view(request):
    # Only allow GET requests
    if request.method == 'GET':
        # Logic to delete past events
        deleted_count, _ = Event.objects.filter(
            date__lt=timezone.now()).delete()
        logger.debug(f"{deleted_count} past events have been deleted.")
        return HttpResponse(f'{deleted_count} past events have been successfully deleted.')
    else:
        return HttpResponse(status=405)  # Method Not Allowed
