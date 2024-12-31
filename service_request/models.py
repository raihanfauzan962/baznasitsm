from django.contrib.auth.models import Group
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from dirtyfields import DirtyFieldsMixin

User = get_user_model()

# Category model to group service items. Each category has a name.
class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name  # String representation returns the category name


# ServiceItem model representing items that can be requested for services.
class ServiceItem(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Each service item belongs to a category.
    image = models.ImageField(upload_to='serviceitems/images/', null=True, blank=True)

    class Meta:
        verbose_name = "Service Item"
        verbose_name_plural = "Service Items"

    def __str__(self):
        return f'{self.name} ({self.category.name})'  # Display service item name along with its category.


# ServiceItemForm model that stores form fields (in JSON format) related to a service item.
class ServiceItemForm(models.Model):
    service_item = models.OneToOneField(ServiceItem, on_delete=models.CASCADE)  # Each service item has one form attached to it.
    form_fields = models.JSONField()  # JSON field to store form data.

    class Meta:
        verbose_name = "Service Item Form"
        verbose_name_plural = "Service Item Forms"

    def __str__(self):
        return f'Form for {self.service_item.name}'  # String representation returns the service item name associated with the form.


# ServiceRequest model for handling service requests submitted by users for service items.
class ServiceRequest(DirtyFieldsMixin, models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('pending', 'Pending'),
        ('pending_customer', 'Pending - Customer'),
        ('pending_assignment', 'Pending - Assignment'),
        ('pending_third_party', 'Pending - Third Party'),
        ('pending_procurement', 'Pending - Procurement'),
        ('assigned', 'Assigned'),
        ('resolved', 'Resolved'),
        ('cancelled', 'Cancelled'),
        ('waiting_approval', 'Waiting on Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('closed', 'Closed'),
    ]

    # Tickets
    ticket_code = models.CharField(max_length=255, unique=True)  # Unique ticket code for the service request.
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='open')  # Status of the request, default is 'open'.

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The user who created the service request.
    group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.SET_NULL)  # Group to which the ticket is assigned.
    assignee = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_requests')  # Single assignee for the ticket.
    
    service_item = models.ForeignKey(ServiceItem, on_delete=models.CASCADE, default=1)  # The service item for which the request is made.
    form_data = models.JSONField()  # JSON field to store the submitted form data related to the request.
    remark = models.TextField(null=True, blank=True)  # Field to store remarks or notes about status changes.

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)  # Timestamp for when the request was created.
    open_at = models.DateTimeField(null=True, blank=True)  # Timestamp for when the request status becomes 'open'.
    pending_at = models.DateTimeField(null=True, blank=True)  # Timestamp for when the request status becomes 'pending'.
    pending_customer_at = models.DateTimeField(null=True, blank=True)  # 'Pending - Customer'.
    pending_assignment_at = models.DateTimeField(null=True, blank=True)  # 'Pending - Assignment'.
    pending_third_party_at = models.DateTimeField(null=True, blank=True)  # 'Pending - Third Party'.
    pending_procurement_at = models.DateTimeField(null=True, blank=True)  # 'Pending - Procurement'.
    assigned_at = models.DateTimeField(null=True, blank=True)  # Timestamp for when the request is assigned.
    resolved_at = models.DateTimeField(null=True, blank=True)  # Timestamp for when the request is resolved.
    cancelled_at = models.DateTimeField(null=True, blank=True)  # Timestamp for when the request is cancelled.
    waiting_approval_at = models.DateTimeField(null=True, blank=True)  # 'Waiting on Approval'.
    approved_at = models.DateTimeField(null=True, blank=True)  # Timestamp for when the request is approved.
    rejected_at = models.DateTimeField(null=True, blank=True)  # Timestamp for when the request is rejected.
    closed_at = models.DateTimeField(null=True, blank=True)  # Timestamp for when the request is closed.

    # Timestamp
    created_at = models.DateTimeField(default=timezone.now)  # Timestamp for when the request was created.
    assigned_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)  # Timestamp for when the request was approved.
    rejected_at = models.DateTimeField(null=True, blank=True)  # Timestamp for when the request was rejected.

    def __str__(self):
        return f'Request by {self.user.username} for {self.service_item.name}'  # String representation for admin and display purposes.

    # Overriding the save method to add custom behavior.
    def save(self, *args, **kwargs):
        """Override save method to generate a unique ticket code and manage status timestamps."""
        # Automatically generate ticket_code if not provided.
        if not self.ticket_code:
            current_year_month = timezone.now().strftime('%Y%m')  # Get the current year and month
            last_ticket = ServiceRequest.objects.filter(ticket_code__startswith=f"SRV-{current_year_month}").order_by('-created_at').first()

            # Check the last ticket of the previous month if no tickets exist for the current month
            if last_ticket:
                last_number = int(last_ticket.ticket_code[-5:]) + 1  # Increment last number by 1
            else:
                # If no ticket exists for the current month, check the last month
                previous_month = (timezone.now() - timezone.timedelta(days=30)).strftime('%Y%m')
                last_month_ticket = ServiceRequest.objects.filter(ticket_code__startswith=f"SRV-{previous_month}").order_by('-created_at').first()
                if last_month_ticket:
                    last_number = int(last_month_ticket.ticket_code[-5:]) + 1  # Increment last number from last month
                else:
                    last_number = 1  # Start from 1 if no tickets exist for the last month

            # Generate the ticket code with 5-digit padding
            self.ticket_code = f"SRV-{current_year_month}{last_number:05d}"

        # Check if the status has changed during an update, and set timestamps accordingly
        if self.pk:  # Only check this for existing records (updates)
            try:
                old_instance = ServiceRequest.objects.get(pk=self.pk)
                if old_instance.status != self.status:  # Status has changed
                    now = timezone.now()  # Current timestamp
                    if self.status == 'open' and not self.open_at:
                        self.open_at = now
                    elif self.status == 'pending' and not self.pending_at:
                        self.pending_at = now
                    elif self.status == 'pending_customer' and not self.pending_customer_at:
                        self.pending_customer_at = now
                    elif self.status == 'pending_assignment' and not self.pending_assignment_at:
                        self.pending_assignment_at = now
                    elif self.status == 'pending_third_party' and not self.pending_third_party_at:
                        self.pending_third_party_at = now
                    elif self.status == 'pending_procurement' and not self.pending_procurement_at:
                        self.pending_procurement_at = now
                    elif self.status == 'assigned' and not self.assigned_at:
                        self.assigned_at = now
                    elif self.status == 'resolved' and not self.resolved_at:
                        self.resolved_at = now
                    elif self.status == 'cancelled' and not self.cancelled_at:
                        self.cancelled_at = now
                    elif self.status == 'waiting_approval' and not self.waiting_approval_at:
                        self.waiting_approval_at = now
                    elif self.status == 'approved' and not self.approved_at:
                        self.approved_at = now
                    elif self.status == 'rejected' and not self.rejected_at:
                        self.rejected_at = now
                    elif self.status == 'closed' and not self.closed_at:
                        self.closed_at = now
            except ServiceRequest.DoesNotExist:
                pass  # Ignore if the record does not exist (new record creation)

        super().save(*args, **kwargs)  # Call the parent class save method to handle saving.
