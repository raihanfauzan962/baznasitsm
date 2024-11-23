from django.urls import path
from . import views

urlpatterns = [
    path('report/new/', views.CreateIncidentReportView.as_view(), name='create_incident_report'),
    path('report/<int:pk>/', views.IncidentReportDetailView.as_view(), name='report_detail'),
    path('my-reports/', views.UserReportsListView.as_view(), name='user_reports'),

    # AJAX URL patterns
    path('ajax/load-subcategories/', views.load_subcategories, name='ajax_load_subcategories'),
    path('ajax/load-issues/', views.load_issues, name='ajax_load_issues'),
    path('ajax/load-affected-devices/', views.load_affected_devices, name='ajax_load_affected_devices'),
    path('ajax/load-floors/', views.load_floors, name='ajax_load_floors'),
]
