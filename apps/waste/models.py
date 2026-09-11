from django.db import models

class WasteRecord(models.Model):
    building_name = models.CharField(max_length=100, default="Central Campus Complex")
    date = models.DateField()
    dry_waste_kg = models.FloatField(default=42.5)
    wet_waste_kg = models.FloatField(default=35.0)
    recyclable_kg = models.FloatField(default=28.0)
    e_waste_kg = models.FloatField(default=2.5)

    class Meta:
        ordering = ['-date']

    def total_kg(self):
        return round(self.dry_waste_kg + self.wet_waste_kg + self.recyclable_kg + self.e_waste_kg, 1)

    def __str__(self):
        return f"{self.building_name} ({self.date}): {self.total_kg()} kg total waste"

class WasteImagePrediction(models.Model):
    class WasteClass(models.TextChoices):
        CARDBOARD = 'CARDBOARD', 'Cardboard'
        GLASS = 'GLASS', 'Glass'
        METAL = 'METAL', 'Metal'
        PAPER = 'PAPER', 'Paper'
        PLASTIC = 'PLASTIC', 'Plastic'
        TRASH = 'TRASH', 'General Trash / Non-Recyclable'

    image = models.ImageField(upload_to='waste_uploads/')
    predicted_class = models.CharField(max_length=30, choices=WasteClass.choices, default=WasteClass.PLASTIC)
    confidence = models.FloatField(default=0.89)
    disposal_recommendation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.predicted_class} ({self.confidence*100:.1f}%) at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
