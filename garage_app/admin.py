from django.contrib import admin
from .models import Car, MaintenanceRequest, ServiceType, Review


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('owner', 'make', 'model', 'year', 'image')

@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('car', 'service', 'requested_date', 'status', 'is_approved')
    list_filter = ('status', 'is_approved', 'service')
    search_fields = ('car__vin', 'car__make', 'car__model')
    ordering = ('-requested_date',)
    list_editable = ('status', 'is_approved')  # ✅ inline editable

@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'request', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'comment')