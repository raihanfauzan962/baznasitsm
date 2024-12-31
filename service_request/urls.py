from django.urls import path
from . import views

urlpatterns = [
    path('', views.ChooseCategoryView.as_view(), name='choose_category'), 
    path('category/<int:category_id>/', views.ChooseServiceItemView.as_view(), name='choose_service_item'), 
    path('request/<int:service_item_id>/', views.PlaceRequestView.as_view(), name='place_request'), 
    path('user_requests/', views.UserRequestsView.as_view(), name='user_requests'), 
    path('request_detail/<int:request_id>/', views.RequestDetailView.as_view(), name='request_detail'), 
]
