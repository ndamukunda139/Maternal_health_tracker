from django.urls import path
from .views import profile, admin_dashboard, login_view, logout_view, RegisterView


urlpatterns = [
    # login and logout routes
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # User registration and profile routes
    path('register/', RegisterView.as_view(), name='register'),

    # User profile and admin dashboard routes
    path('profile/', profile, name='profile'),  
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'), 
     
]