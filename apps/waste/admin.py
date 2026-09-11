from django.contrib import admin
from .models import WasteRecord, WasteImagePrediction

@admin.register(WasteRecord)
class WasteRecordAdmin(admin.ModelAdmin):
    list_display = ('building_name', 'date', 'dry_waste_kg', 'wet_waste_kg', 'recyclable_kg', 'total_kg')

@admin.register(WasteImagePrediction)
class WasteImagePredictionAdmin(admin.ModelAdmin):
    list_display = ('predicted_class', 'confidence', 'created_at')
    list_filter = ('predicted_class',)
