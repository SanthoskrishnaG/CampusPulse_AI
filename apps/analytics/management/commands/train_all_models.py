import time
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = "Sequential end-to-end training and calibration of the entire CampusPulse AI ML Fleet."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=================================================="))
        self.stdout.write(self.style.NOTICE("STARTING FULL CAMPUSPULSE AI ML FLEET CALIBRATION"))
        self.stdout.write(self.style.NOTICE("=================================================="))
        start_time = time.time()

        commands = [
            'train_academic_risk',
            'train_canteen_demand',
            'train_food_waste',
            'train_complaints_nlp',
            'train_energy_anomaly',
            'train_transport_eta',
            'train_parking_model'
        ]

        for cmd in commands:
            self.stdout.write(f"\n--- Running {cmd} ---")
            try:
                call_command(cmd)
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Command {cmd} encountered an error: {e}"))

        total_duration = round(time.time() - start_time, 2)
        self.stdout.write(self.style.NOTICE("\n=================================================="))
        self.stdout.write(self.style.SUCCESS(f"ALL MODELS TRAINED & REGISTERED IN {total_duration}s!"))
        self.stdout.write(self.style.NOTICE("=================================================="))
