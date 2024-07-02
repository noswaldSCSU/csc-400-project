from django.urls import path
from . import views
from .views import start_trial, save_response
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('start-experiment/<int:participant_id>/', views.start_experiment, name='start_experiment'),
    path('start_trial/', start_trial, name='start_trial'),
    path('save_response/', save_response, name='save_response'),
    path('experiment-complete/', views.experiment_complete, name='experiment_complete'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('experiment/<int:experiment_id>/', views.experiment_view, name='experiment'),
]

