from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import ListView, DetailView, FormView, View

from django.utils import timezone
from datetime import timedelta

from .models import Category, Asset, AssetForm, ServiceRequest
from .forms import DynamicServiceRequestForm

# View to choose a category (ListView)
class ChooseCategoryView(ListView):
    model = Category
    template_name = 'service_request/choose_category.html'
    context_object_name = 'categories'

# View to list assets under a specific category, with search functionality
class ChooseAssetView(View):
    def get(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        assets = Asset.objects.filter(category=category)

        # Get the search query from request parameters
        search_query = request.GET.get('search_query', '')
        if search_query:
            # Filter assets based on the search query (case insensitive)
            assets = assets.filter(name__icontains=search_query)

        # Pass assets, category, and the search query back to the template
        context = {
            'assets': assets,
            'category': category,
            'search_query': search_query,
        }
        return render(request, 'service_request/choose_asset.html', context)


# View to place a request by choosing an asset and dynamically loading the form
class PlaceRequestView(LoginRequiredMixin, FormView):
    template_name = 'service_request/place_request.html'
    form_class = DynamicServiceRequestForm

    def get_asset(self):
        asset_id = self.kwargs.get('asset_id')
        return get_object_or_404(Asset, id=asset_id)

    def get_form_kwargs(self):
        asset = self.get_asset()
        asset_form = get_object_or_404(AssetForm, asset=asset)
        kwargs = super().get_form_kwargs()
        kwargs['asset_form'] = asset_form.form_fields
        return kwargs

    def form_valid(self, form):
        asset = self.get_asset()
        service_request = ServiceRequest.objects.create(
            user=self.request.user,
            asset=asset,
            form_data=form.cleaned_data
        )
        # Pass the request_id to the redirect
        return redirect('request_detail', request_id=service_request.id)


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

