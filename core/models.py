from django.db import models
from django.contrib.auth.models import User

class NGO(models.Model):
    CATEGORY_CHOICES = [
        ('education', 'Education'),
        ('health', 'Healthcare'),
        ('environment', 'Environment'),
        ('food', 'Food & Nutrition'),
        ('women', "Women Empowerment"),
        ('disaster', 'Disaster Relief'),
        ('animal', 'Animal Welfare'),
    ]
    STATUS_CHOICES = [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')]

    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=200)
    founded_year = models.IntegerField(default=2020)
    registration_number = models.CharField(max_length=100, unique=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    website = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verified = models.BooleanField(default=False)
    logo_initial = models.CharField(max_length=3, default='NGO')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def total_received(self):
        return sum(d.amount for d in self.donations.filter(status='completed'))

    @property
    def donor_count(self):
        return self.donations.filter(status='completed').values('donor').distinct().count()


class Need(models.Model):
    PRIORITY_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')]
    ngo = models.ForeignKey(NGO, on_delete=models.CASCADE, related_name='needs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    amount_required = models.DecimalField(max_digits=12, decimal_places=2)
    amount_raised = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    deadline = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.ngo.name} - {self.title}"

    @property
    def percentage(self):
        if self.amount_required > 0:
            return min(int((self.amount_raised / self.amount_required) * 100), 100)
        return 0


class Donation(models.Model):
    TYPE_CHOICES = [('monetary', 'Monetary'), ('material', 'Material')]
    STATUS_CHOICES = [('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')]

    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations')
    ngo = models.ForeignKey(NGO, on_delete=models.CASCADE, related_name='donations')
    need = models.ForeignKey(Need, on_delete=models.SET_NULL, null=True, blank=True, related_name='donations')
    donation_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='monetary')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    material_description = models.TextField(blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"Donation by {self.donor.username} to {self.ngo.name}"


class UtilizationReport(models.Model):
    ngo = models.ForeignKey(NGO, on_delete=models.CASCADE, related_name='reports')
    need = models.ForeignKey(Need, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    amount_used = models.DecimalField(max_digits=12, decimal_places=2)
    impact_description = models.TextField()
    beneficiaries_count = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ngo.name} - {self.title}"
