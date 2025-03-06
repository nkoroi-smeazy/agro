import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import County, Ward, Locality, Farmer, Farm, FarmProduce
from core.utils import assign_to_cig  # Ensure this function is defined as per your business logic

User = get_user_model()

class Command(BaseCommand):
    help = "Generate dummy data for Machakos County with 40 wards, 5 localities per ward, and farms with multiple FarmProduce entries."

    def handle(self, *args, **options):
        self.stdout.write("Starting dummy data generation for Machakos County...")

        # Create Machakos County
        machakos, created = County.objects.get_or_create(name="Machakos County")
        if created:
            self.stdout.write("Created County: Machakos County")
        else:
            self.stdout.write("Machakos County already exists.")

        # Predefined produce types
        produce_types = ["Maize", "Beans", "Cabbage", "Chicken", "Dairy"]

        # Create 40 wards, each with 5 localities
        for ward_num in range(1, 41):  # Wards 1 to 40
            ward, _ = Ward.objects.get_or_create(name=f"Ward {ward_num}", county=machakos)
            self.stdout.write(f"Created/Found {ward.name}")

            for loc_num in range(1, 6):  # 5 localities per ward
                locality, _ = Locality.objects.get_or_create(name=f"Locality {ward_num}-{loc_num}", ward=ward)
                self.stdout.write(f"  Created/Found {locality.name}")

                # Create an agro-technician for this locality if not exists
                agro_username = f"agrotech_{ward_num}_{loc_num}"
                if not User.objects.filter(username=agro_username).exists():
                    User.objects.create_user(
                        username=agro_username,
                        email=f"{agro_username}@example.com",
                        password="password123",
                        user_type="agro"
                    )
                    self.stdout.write(f"    Created Agro-Technician: {agro_username}")

                # Decide number of farms for this locality:
                # For Locality 1-1, create 40 farms to simulate the CIG threshold.
                if ward_num == 1 and loc_num == 1:
                    num_farms = 40
                else:
                    num_farms = 10

                for farm_num in range(1, num_farms + 1):
                    farmer_username = f"farmer_{ward_num}_{loc_num}_{farm_num}"
                    if not User.objects.filter(username=farmer_username).exists():
                        farmer_user = User.objects.create_user(
                            username=farmer_username,
                            email=f"{farmer_username}@example.com",
                            password="password123",
                            user_type="farmer"
                        )
                        farmer_obj = Farmer.objects.create(user=farmer_user, contact_number="0712345678")
                        self.stdout.write(f"    Created Farmer: {farmer_username}")

                        # Create a Farm for this Farmer
                        farm = Farm.objects.create(farmer=farmer_obj, name=f"Farm {ward_num}-{loc_num}-{farm_num}", locality=locality)
                        self.stdout.write(f"      Created Farm: Farm {ward_num}-{loc_num}-{farm_num}")

                        # Create FarmProduce entries for the farm:
                        # For the special locality (Locality 1-1), force one produce as "Maize" to simulate hitting the max of 35.
                        produce_list = []
                        if ward_num == 1 and loc_num == 1:
                            produce_list.append("Maize")
                            # Optionally, add more random produce types (avoid duplicate "Maize")
                            remaining = random.randint(0, 2)
                            other_produces = [pt for pt in produce_types if pt != "Maize"]
                            produce_list += random.sample(other_produces, k=min(remaining, len(other_produces)))
                        else:
                            # For other localities, each farm gets between 1 and 3 produce types.
                            num_produces = random.randint(1, 3)
                            produce_list = random.sample(produce_types, k=num_produces)

                        for prod in produce_list:
                            quantity = random.randint(10, 100)
                            farm_produce = FarmProduce.objects.create(
                                farm=farm,
                                produce_type=prod,
                                quantity=quantity
                            )
                            # Automatically assign the FarmProduce to a CIG based on your business logic.
                            assign_to_cig(farm_produce)
                            self.stdout.write(f"        Created FarmProduce: {prod} (quantity: {quantity})")
        
        self.stdout.write("Dummy data generation complete.")
