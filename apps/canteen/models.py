from django.db import models

class Canteen(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30, unique=True, help_text="e.g. CANTEEN-MAIN, CAFE-SOUTH")
    location_name = models.CharField(max_length=100, default="Central Dining Hall")
    seating_capacity = models.PositiveIntegerField(default=350)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class MenuItem(models.Model):
    class MealCategory(models.TextChoices):
        BREAKFAST = 'BREAKFAST', 'Breakfast'
        LUNCH = 'LUNCH', 'Lunch Thali / Meals'
        SNACKS = 'SNACKS', 'Evening Snacks & Tea'
        DINNER = 'DINNER', 'Dinner'

    canteen = models.ForeignKey(Canteen, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=30, choices=MealCategory.choices, default=MealCategory.LUNCH)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=50.00)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()} - Rs. {self.price})"

class MealRecord(models.Model):
    class MealType(models.TextChoices):
        BREAKFAST = 'BREAKFAST', 'Breakfast'
        LUNCH = 'LUNCH', 'Lunch'
        SNACKS = 'SNACKS', 'Snacks'
        DINNER = 'DINNER', 'Dinner'

    canteen = models.ForeignKey(Canteen, on_delete=models.CASCADE, related_name='meal_records')
    date = models.DateField()
    meal_type = models.CharField(max_length=30, choices=MealType.choices, default=MealType.LUNCH)
    meals_prepared = models.PositiveIntegerField(default=300)
    meals_sold = models.PositiveIntegerField(default=285)
    leftover_waste_kg = models.FloatField(default=6.5)
    is_event_day = models.BooleanField(default=False)
    weather_condition = models.CharField(max_length=50, default="Clear")

    class Meta:
        ordering = ['-date', 'meal_type']
        unique_together = ('canteen', 'date', 'meal_type')

    def __str__(self):
        return f"{self.canteen.code} {self.date} [{self.meal_type}]: {self.meals_sold}/{self.meals_prepared} sold (Waste: {self.leftover_waste_kg} kg)"
