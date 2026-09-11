from django.contrib import admin
from .models import Canteen, MenuItem, MealRecord

@admin.register(Canteen)
class CanteenAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'location_name', 'seating_capacity')

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'canteen', 'category', 'price', 'is_available')
    list_filter = ('category', 'is_available')

@admin.register(MealRecord)
class MealRecordAdmin(admin.ModelAdmin):
    list_display = ('canteen', 'date', 'meal_type', 'meals_prepared', 'meals_sold', 'leftover_waste_kg')
    list_filter = ('meal_type', 'date')
