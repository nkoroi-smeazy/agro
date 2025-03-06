import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum
from django.contrib.auth import get_user_model
from core.models import (
    County, Ward, Locality, Farmer, Farm, FarmProduce,
    AgriculturalCycle, CommonInterestGroup
)
from core.utils import assign_to_cig_bulk  # Use the new bulk function

User = get_user_model()

class Command(BaseCommand):
    help = ("Generate enriched dummy data for Machakos County with 40 wards, 5 localities per ward, "
            "an Agro-Technician per locality, multiple Farmers (with multiple Farms), "
            "FarmProduce entries, and AgriculturalCycles for each CIG.")

    def handle(self, *args, **options):
        self.stdout.write("Starting dummy data generation for Machakos County...")
        with transaction.atomic():
            # Create Machakos County
            machakos, _ = County.objects.get_or_create(name="Machakos County")
            self.stdout.write("Ensured Machakos County exists.")

            produce_types = ["Maize", "Beans", "Cabbage", "Chicken", "Dairy"]

            # Containers to collect objects for bulk creation
            farms_to_create = []       # unsaved Farm instances
            farm_produce_data = []     # dicts for FarmProduce creation
            localities_list = []

            # Process wards and localities
            for ward_num in range(1, 41):
                ward, _ = Ward.objects.get_or_create(name=f"Ward {ward_num}", county=machakos)
                self.stdout.write(f"Processing {ward.name}")

                for loc_num in range(1, 6):
                    locality, _ = Locality.objects.get_or_create(name=f"Locality {ward_num}-{loc_num}", ward=ward)
                    localities_list.append(locality)

                    # Create or update Agro-Technician for locality
                    agro_username = f"agrotech_{ward_num}_{loc_num}"
                    agro_user = User.objects.filter(username=agro_username).first()
                    if not agro_user:
                        agro_user = User.objects.create_user(
                            username=agro_username,
                            email=f"{agro_username}@example.com",
                            password="password123",
                            user_type="agro"
                        )
                        self.stdout.write(f"  Created Agro-Technician: {agro_username}")
                    agro_user.locality = locality
                    agro_user.save()
                    locality.agro_technician = agro_user
                    locality.save()

                    # Create between 5 and 10 farmers for this locality
                    num_farmers = random.randint(5, 10)
                    for i in range(1, num_farmers + 1):
                        farmer_username = f"farmer_{ward_num}_{loc_num}_{i}"
                        farmer_user = User.objects.filter(username=farmer_username).first()
                        if not farmer_user:
                            farmer_user = User.objects.create_user(
                                username=farmer_username,
                                email=f"{farmer_username}@example.com",
                                password="password123",
                                user_type="farmer"
                            )
                            self.stdout.write(f"  Created Farmer: {farmer_username}")
                        farmer_user.locality = locality
                        farmer_user.save()
                        if not hasattr(farmer_user, 'farmer_profile'):
                            Farmer.objects.create(user=farmer_user, contact_number="0712345678")

                        # For each farmer, create between 1 and 3 farms
                        num_farms = random.randint(1, 3)
                        for j in range(1, num_farms + 1):
                            farm_name = f"Farm_{ward_num}-{loc_num}-{farmer_username}-{j}"
                            farms_to_create.append(Farm(
                                farmer=farmer_user.farmer_profile,
                                name=farm_name,
                                locality=locality,
                                latitude=random.uniform(-5.0, 5.0),
                                longitude=random.uniform(36.0, 37.0)
                            ))
                            # For each farm, create produce entries
                            if ward_num == 1 and loc_num == 1:
                                produce_list = ["Maize"]
                                remaining = random.randint(0, 2)
                                other_produces = [pt for pt in produce_types if pt != "Maize"]
                                produce_list += random.sample(other_produces, k=min(remaining, len(other_produces)))
                            else:
                                num_produces = random.randint(1, 3)
                                produce_list = random.sample(produce_types, k=num_produces)
                            for prod in produce_list:
                                farm_produce_data.append({
                                    'farm_name': farm_name,  # temporary key to link after bulk create
                                    'produce_type': prod,
                                    'total_units': random.randint(10, 100),
                                    'unit_of_measure': 'kg'
                                })

            # Bulk create Farms
            created_farms = Farm.objects.bulk_create(farms_to_create)
            self.stdout.write(f"Bulk created {len(created_farms)} farms.")

            # Build a mapping from farm name to Farm instance for linking produces
            farm_mapping = {farm.name: farm for farm in created_farms}

            # Prepare FarmProduce objects list
            farm_produce_objs = []
            for fp in farm_produce_data:
                farm_instance = farm_mapping.get(fp['farm_name'])
                if farm_instance:
                    farm_produce_objs.append(FarmProduce(
                        farm=farm_instance,
                        produce_type=fp['produce_type'],
                        total_units=fp['total_units'],
                        unit_of_measure=fp['unit_of_measure']
                    ))
            created_farm_produces = FarmProduce.objects.bulk_create(farm_produce_objs)
            self.stdout.write(f"Bulk created {len(created_farm_produces)} farm produce records.")

            # Use the bulk function to assign each FarmProduce to a CIG
            assign_to_cig_bulk(created_farm_produces)
            self.stdout.write("Assigned all FarmProduce to appropriate CIGs using bulk function.")

            # For each Farm, update its many-to-many "cigs" field from its produce assignments
            for farm in created_farms:
                cigs = {fp.cig for fp in farm.farm_produces.all() if fp.cig is not None}
                if cigs:
                    farm.cigs.set(list(cigs))
            self.stdout.write("Updated farms with associated CIGs.")

            # Create AgriculturalCycles for each CIG without one and update aggregates
            self.stdout.write("Creating AgriculturalCycles for each CIG...")
            cigs = CommonInterestGroup.objects.all()
            for cig in cigs:
                if not cig.current_cycle:
                    start_week = "WK1_2025"
                    end_week = "WK8_2025"
                    cycle = AgriculturalCycle.objects.create(
                        start_week=start_week,
                        end_week=end_week,
                        cig=cig,
                        farm_produce=None
                    )
                    cig.current_cycle = cycle
                    # Update aggregate fields
                    cig.number_of_farms = cig.farms_registered.count()
                    cig.unit_of_measure = "kg"
                    related_produces = FarmProduce.objects.filter(cig=cig, agricultural_cycle__isnull=True)
                    total_units = related_produces.aggregate(sum_total=Sum('total_units'))['sum_total'] or 0
                    related_produces.update(agricultural_cycle=cycle)
                    cig.total_units_current_cycle = total_units
                    cig.total_units_last_cycle = random.randint(0, 500)
                    cig.save()
                    self.stdout.write(f"  Created AgriculturalCycle for CIG: {cig}")
                else:
                    self.stdout.write(f"  CIG already has an AgriculturalCycle: {cig}")

        self.stdout.write("Dummy data generation complete.")
