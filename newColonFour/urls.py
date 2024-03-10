# yourapp/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from .views import HomePageView, register, org_verification, OrganizerProfileDetailView, CustomLoginView, DancerCreateView, BattleCreate, SearchHomePage

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




    # Add other URL patterns as needed
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
