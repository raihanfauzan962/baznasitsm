from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserDashboardView.as_view(), name='user_dashboard'),
]
