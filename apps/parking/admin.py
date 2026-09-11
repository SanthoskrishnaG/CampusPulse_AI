from django.contrib import admin
from .models import ParkingLot, ParkingSlot

@admin.register(ParkingLot)
class ParkingLotAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'total_slots', 'latitude', 'longitude', 'is_active')

@admin.register(ParkingSlot)
class ParkingSlotAdmin(admin.ModelAdmin):
    list_display = ('slot_number', 'lot', 'slot_type', 'is_occupied', 'updated_at')
    list_filter = ('lot', 'slot_type', 'is_occupied')
