from django.db import models

class ParkingLot(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30, unique=True, help_text="e.g. PKG-NORTH, PKG-AUDITORIUM")
    total_slots = models.PositiveIntegerField(default=60)
    latitude = models.FloatField(default=11.0285)
    longitude = models.FloatField(default=77.0270)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def occupied_count(self):
        return self.slots.filter(is_occupied=True).count()

    def available_count(self):
        return max(0, self.total_slots - self.occupied_count())

    def occupancy_percentage(self):
        if self.total_slots == 0:
            return 0.0
        return round((self.occupied_count() / self.total_slots) * 100.0, 1)

class ParkingSlot(models.Model):
    class SlotType(models.TextChoices):
        CAR = 'CAR', 'Standard Car'
        MOTORCYCLE = 'MOTORCYCLE', 'Two-Wheeler'
        EV_CHARGING = 'EV_CHARGING', 'Electric Vehicle Charging'
        ACCESSIBLE = 'ACCESSIBLE', 'Accessible / Handicap'

    lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE, related_name='slots')
    slot_number = models.CharField(max_length=20)
    slot_type = models.CharField(max_length=20, choices=SlotType.choices, default=SlotType.CAR)
    is_occupied = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('lot', 'slot_number')
        ordering = ['lot', 'slot_number']

    def __str__(self):
        status = "Occupied" if self.is_occupied else "Available"
        return f"{self.lot.code} #{self.slot_number} [{status}]"
