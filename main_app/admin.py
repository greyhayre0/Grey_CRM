'''from django.contrib import admin

from .models import Client, Service, Deal, AdditionalContact, Comment

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'created_at']
    search_fields = ['name', 'phone', 'email']
    list_filter = ['created_at']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration_days', 'is_active']
    list_editable = ['price', 'is_active']
    list_filter = ['is_active']

@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ['client', 'service', 'status',
    'price', 'start_date', 'end_date']
    list_filter = ['status', 'start_date', 'end_date']
    search_fields = ['client__name', 'service__name']
    date_hierarchy = 'created_at'

admin.site.register(AdditionalContact)
admin.site.register(Comment)
'''
