# api/admin.py
from django.contrib import admin
from .models import User, Service, ServicePriceMatrix, AppointmentSlot, Booking, BookingLog


class ServicePriceMatrixInline(admin.TabularInline):
    model = ServicePriceMatrix
    extra = 6
    max_num = 6

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'estimated_duration_hours')
    search_fields = ('name',)
    inlines = [ServicePriceMatrixInline]

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'service', 'vehicle_category', 'final_price', 'status', 'requested_date')
    list_filter = ('status', 'vehicle_category', 'requested_date')
    search_fields = ('user__email', 'vehicle_make_model')

admin.site.register(User)
admin.site.register(AppointmentSlot)
admin.site.register(BookingLog)