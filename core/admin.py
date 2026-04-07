from django.contrib import admin
from .models import NGO, Need, Donation, UtilizationReport

@admin.register(NGO)
class NGOAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'location', 'status', 'verified']
    list_filter = ['status', 'category', 'verified']
    search_fields = ['name', 'location']

@admin.register(Need)
class NeedAdmin(admin.ModelAdmin):
    list_display = ['title', 'ngo', 'amount_required', 'amount_raised', 'priority']

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['donor', 'ngo', 'amount', 'status', 'created_at']

@admin.register(UtilizationReport)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['ngo', 'title', 'amount_used', 'beneficiaries_count']
