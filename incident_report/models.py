from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from dirtyfields import DirtyFieldsMixin
import os

User = get_user_model()

# Model representing a category (e.g. Hardware, Software)
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Model representing a sub-category linked to a Category
class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Model representing issues linked to a Sub-Category
class Issue(models.Model):
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='issues')
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

# Model representing affected devices linked to Issues
class AffectedDevice(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='devices')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Model representing buildings
class Building(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Model representing floors linked to Buildings
class Floor(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='floors')
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

# Model for incident reports (tickets)
class IncidentReport(DirtyFieldsMixin, models.Model):
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
    
    ticket_code = models.CharField(max_length=255, unique=True)  # Unique identifier for the ticket

    requester = models.ForeignKey(User, on_delete=models.CASCADE)  # Requester is the logged-in user
    request_for = models.EmailField(blank=True, null=True)  # Optional email field
    contact_person = models.CharField(max_length=20, blank=True, null=True)  # Optional contact number
    
    # Ticket fields
    group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.SET_NULL)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')  # User assigned to resolve the ticket
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')  # Current status of the ticket
    
    # Foreign keys for categorizing the incident
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.PROTECT)
    issue = models.ForeignKey(Issue, on_delete=models.PROTECT)
    affected_device = models.ForeignKey(AffectedDevice, on_delete=models.PROTECT)
    
    building = models.ForeignKey(Building, on_delete=models.PROTECT)
    floor = models.ForeignKey(Floor, on_delete=models.PROTECT)
    
    # Additional fields for the incident report
    subject = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)  # Validate file size elsewhere
    remark = models.TextField(blank=True, null=True)  # New field for additional remarks
    
    # Timestamps for tracking the ticket lifecycle
    created_at = models.DateTimeField(default=timezone.now)
    open_at = models.DateTimeField(null=True, blank=True)
    pending_at = models.DateTimeField(null=True, blank=True)
    pending_customer_at = models.DateTimeField(null=True, blank=True)
    pending_assignment_at = models.DateTimeField(null=True, blank=True)
    pending_third_party_at = models.DateTimeField(null=True, blank=True)
    pending_procurement_at = models.DateTimeField(null=True, blank=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    waiting_approval_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        """Validate file size and extension."""
        if self.attachment:
            self.validate_file_size()
            self.validate_file_extension()

    def validate_file_size(self):
        max_size_mb = 5
        if self.attachment.size > max_size_mb * 1024 * 1024:
            raise ValidationError(f"File size must be under {max_size_mb}MB.")

    def validate_file_extension(self):
        allowed_extensions = ['pdf', 'csv', 'jpeg', 'jpg', 'png', 'xlsx']
        ext = os.path.splitext(self.attachment.name)[1][1:].lower()
        if ext not in allowed_extensions:
            raise ValidationError(f"Allowed file types are: {', '.join(allowed_extensions)}.")
    
    def __str__(self):
        return self.ticket_code  # Return ticket code as string representation

    def save(self, *args, **kwargs):
        """Override save method to generate a unique ticket code and manage status timestamps."""
        # Generate ticket code only when creating a new ticket
        if not self.ticket_code:
            current_year_month = timezone.now().strftime('%Y%m')  # Get current year and month
            last_ticket = IncidentReport.objects.filter(ticket_code__startswith=f"INC-{current_year_month}").order_by('-created_at').first()
            
            # Check the last ticket of the previous month
            if last_ticket:
                last_number = int(last_ticket.ticket_code[-5:]) + 1  # Increment last 5 digits
            else:
                # If no ticket exists for the current month, check the last month
                previous_month = (timezone.now() - timezone.timedelta(days=30)).strftime('%Y%m')
                last_month_ticket = IncidentReport.objects.filter(ticket_code__startswith=f"INC-{previous_month}").order_by('-created_at').first()
                if last_month_ticket:
                    last_number = int(last_month_ticket.ticket_code[-5:]) + 1  # Increment last 5 digits from last month
                else:
                    last_number = 1  # Start from 1 if no tickets exist for the last month

            # Create the new ticket code with 5-digit padding
            self.ticket_code = f"INC-{current_year_month}{last_number:05d}"
        
        # Update timestamps based on status changes
        if self.pk:
            old_instance = IncidentReport.objects.get(pk=self.pk)
            if old_instance.status != self.status:
                now = timezone.now()
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
        
        super().save(*args, **kwargs)  # Call the parent save method

