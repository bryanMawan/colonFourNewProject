# yourapp/urls.py
# Standard Library Imports
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth.views import LogoutView

# Local Application Imports
from .views import (
    HomePageView,
    fetch_suboptions,
    register,
    org_verification,
    create_dancer,
    OrganizerProfileDetailView,
    CustomLoginView,
    DancerCreateView,
    BattleCreate,
    SearchHomePage,
    CreateTipView,
    send_code_view,
    verify_code_view,
    get_event_details,
    cleanup_view,
    EventAjaxView, 
    get_partial_content,
    TipsListView
)
urlpatterns = [
    path('oldhome/', HomePageView.as_view(), name='oldhome'),
    path('login/', CustomLoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('', SearchHomePage.as_view(), name='home'),
    path('organizer/<slug:slug>/', OrganizerProfileDetailView.as_view(), name='organizer-profile-detail'),
    path('org-verification/', org_verification, name='org_verification'),
    path('register/', register, name='register'),  # Add this line
    path('dancer/create/', DancerCreateView.as_view(), name='create_dancer'),
    path('battle/create/', BattleCreate.as_view(), name='create_battle'),  # Add this line for battle creation
    path('send-code/', send_code_view, name='send_code'),
    path('verify-code/', verify_code_view, name='verify_code'),
    path('tip/create/', CreateTipView.as_view(), name='create_tip'),
    path('search/', SearchHomePage.as_view(), name='search_home_page'),
    path('fetch_suboptions/', fetch_suboptions, name='fetch_suboptions'),
    path('get_event_details/<int:event_id>/', get_event_details, name='get_event_details'),
    path('cleanup/', cleanup_view, name='cleanup_view'),
    path('create-dancer/', create_dancer, name='dancer_create'),
    path('events/', EventAjaxView.as_view(), name='event_ajax_view'),
    path('get_partial_content/', get_partial_content, name='get_partial_content'),
    path('tips/all', TipsListView.as_view(), name='tips-list'),




    # Add other URL patterns as needed
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
