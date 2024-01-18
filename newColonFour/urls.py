# yourapp/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import HomePageView, register, org_verification, OrganizerProfileDetailView, CustomLoginView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('login/', CustomLoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('organizer/<slug:slug>/', OrganizerProfileDetailView.as_view(), name='organizer-profile-detail'),

    path('org-verification/', org_verification, name='org_verification'),
    path('register/', register, name='register'),  # Add this line


    # Add other URL patterns as needed
]
