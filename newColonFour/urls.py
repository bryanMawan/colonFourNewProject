# yourapp/urls.py
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import HomePageView, register, org_verification

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('org-verification/', org_verification, name='org_verification'),
    path('register/', register, name='register'),  # Add this line


    # Add other URL patterns as needed
]
