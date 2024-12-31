from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import ListView, DetailView, FormView, View

from django.utils import timezone
from datetime import timedelta

from .models import Category, ServiceItem, ServiceItemForm, ServiceRequest
from .forms import DynamicServiceRequestForm

# View to choose a category (ListView)
class ChooseCategoryView(ListView):
    model = Category
    template_name = 'service_request/choose_category.html'
    context_object_name = 'categories'


# View to list service items under a specific category, with search functionality
class ChooseServiceItemView(View):
    def get(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        service_items = ServiceItem.objects.filter(category=category)

        # Get the search query from request parameters
        search_query = request.GET.get('search_query', '')
        if search_query:
            # Filter service items based on the search query (case insensitive)
            service_items = service_items.filter(name__icontains=search_query)

        # Pass service items, category, and the search query back to the template
        context = {
            'service_items': service_items,
            'category': category,
            'search_query': search_query,
        }
        return render(request, 'service_request/choose_service_item.html', context)


# View to place a request by choosing a service item and dynamically loading the form
class PlaceRequestView(LoginRequiredMixin, FormView):
    template_name = 'service_request/place_request.html'
    form_class = DynamicServiceRequestForm

    def get_service_item(self):
        service_item_id = self.kwargs.get('service_item_id')
        return get_object_or_404(ServiceItem, id=service_item_id)

    def get_form_kwargs(self):
        service_item = self.get_service_item()
        service_item_form = get_object_or_404(ServiceItemForm, service_item=service_item)
        kwargs = super().get_form_kwargs()
        kwargs['service_item_form'] = service_item_form.form_fields
        return kwargs

    def form_valid(self, form):
        service_item = self.get_service_item()
        service_request = ServiceRequest.objects.create(
            user=self.request.user,
            service_item=service_item,
            form_data=form.cleaned_data
        )
        # Pass the request_id to the redirect
        return redirect('request_detail', request_id=service_request.id)


# View for user-specific requests
class UserRequestsView(LoginRequiredMixin, ListView):
    model = ServiceRequest
    template_name = 'service_request/user_requests.html'
    context_object_name = 'requests'

    def get_queryset(self):
        queryset = ServiceRequest.objects.filter(user=self.request.user)

        # Filtering logic
        filter_option = self.request.GET.get('filter', 'all')
        status_filter = self.request.GET.get('status', 'all')
        today = timezone.now().date()
        start_date = None

        # Date range filtering
        if filter_option == 'today':
            start_date = today
        elif filter_option == 'yesterday':
            start_date = today - timedelta(days=1)
        elif filter_option == '7_days':
            start_date = today - timedelta(days=7)
        elif filter_option == '30_days':
            start_date = today - timedelta(days=30)

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        # Status filtering
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by('-created_at')


# View to show request details
class RequestDetailView(LoginRequiredMixin, DetailView):
    model = ServiceRequest
    template_name = 'service_request/request_detail.html'
    context_object_name = 'service_request'

    def get_object(self, queryset=None):
        # Get the request_id from the URL kwargs
        request_id = self.kwargs.get('request_id')
        # Use get_object_or_404 to ensure it raises a 404 if not found
        return get_object_or_404(ServiceRequest, id=request_id, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_request = self.get_object()

        # Add timestamps to the context
        context['timestamps'] = [
            ('open_at', 'Open At'),
            ('pending_at', 'Pending At'),
            ('pending_customer_at', 'Pending Customer At'),
            ('pending_assignment_at', 'Pending Assignment At'),
            ('pending_third_party_at', 'Pending Third Party At'),
            ('pending_procurement_at', 'Pending Procurement At'),
            ('assigned_at', 'Assigned At'),
            ('resolved_at', 'Resolved At'),
            ('cancelled_at', 'Cancelled At'),
            ('waiting_approval_at', 'Waiting Approval At'),
            ('approved_at', 'Approved At'),
            ('rejected_at', 'Rejected At'),
            ('closed_at', 'Closed At'),
        ]

        # Dynamically add timestamp values
        context['timestamp_values'] = {
            timestamp: getattr(service_request, timestamp, None)
            for timestamp, _ in context['timestamps']
        }

        return context
