from django.urls import path
from . import views
from .views import create_trial_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('experiment-complete/', views.experiment_complete, name='experiment_complete'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('experiment/<int:experiment_id>/', views.experiment_view, name='experiment'),
    path('create_trial/', create_trial_view, name='create_trial'),
]

