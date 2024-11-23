from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from dirtyfields import DirtyFieldsMixin

User = get_user_model()

# Category model to group assets. Each category has a name.
class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name  # String representation returns the category name

# Asset model representing items that can be requested for services.
class Asset(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Each asset belongs to a category.
    pic = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Asset has a person in charge (PIC), optional field.
    image = models.ImageField(upload_to='assets/images/', null=True, blank=True)

    class Meta:
        verbose_name = "Service Item"
        verbose_name_plural = "Service Items"
    
    def __str__(self):
        return f'{self.name} ({self.category.name})'  # Display asset name along with its category.

# AssetForm model that stores form fields (in JSON format) related to an asset.
class AssetForm(models.Model):
    asset = models.OneToOneField(Asset, on_delete=models.CASCADE)  # Each asset has one form attached to it.
    form_fields = models.JSONField()  # JSON field to store form data.

    class Meta:
        verbose_name = "Service Item Form"
        verbose_name_plural = "Service Item Forms"
    
    def __str__(self):
        return f'Form for {self.asset.name}'  # String representation returns the asset name associated with the form.

# ServiceRequest model for handling service requests submitted by users for assets.
class ServiceRequest(DirtyFieldsMixin, models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),  # Initial state when the request is created.
        ('approved', 'Approved'),  # State when the request is approved.
        ('rejected', 'Rejected'),  # State when the request is rejected.
    ]
    
    # Tickets
    ticket_code = models.CharField(max_length=255, unique=True)  # Unique ticket code for the service request.
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')  # Status of the request, default is 'pending'.
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The user who created the service request.
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)  # The asset for which the request is made.
    form_data = models.JSONField()  # JSON field to store the submitted form data related to the request.
    
    # Timestamp
    created_at = models.DateTimeField(default=timezone.now)  # Timestamp for when the request was created.
    approved_at = models.DateTimeField(null=True, blank=True)  # Timestamp for when the request was approved.
    rejected_at = models.DateTimeField(null=True, blank=True)  # Timestamp for when the request was rejected.

    def __str__(self):
        return f'Request by {self.user.username} for {self.asset.name}'  # String representation for admin and display purposes.

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
                    if self.status == 'approved' and not self.approved_at:  # Set approved_at if status is approved
                        self.approved_at = timezone.now()
                    elif self.status == 'rejected' and not self.rejected_at:  # Set rejected_at if status is rejected
                        self.rejected_at = timezone.now()
            except ServiceRequest.DoesNotExist:
                pass  # Ignore if the record does not exist (new record creation)

        super().save(*args, **kwargs)  # Call the parent class save method to handle saving

