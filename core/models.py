from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models import Sum, Count

# CUSTOM USER MODEL
class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('farmer', 'Farmer'),
        ('agro', 'Agro-Technician'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    # For Agro-Technicians, link to the Locality they manage (optional)
    locality = models.ForeignKey('Locality', on_delete=models.SET_NULL, null=True, blank=True, related_name='agro_technicians')
    # Which CIGs this agro-tech manages
    managed_cigs = models.ManyToManyField('CommonInterestGroup', blank=True, related_name='managing_agrotechs')
    
    # Override groups and user_permissions to avoid reverse accessor conflicts
    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="custom_user_set",
        help_text="The groups this user belongs to.",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="custom_user_set",
        help_text="Specific permissions for this user.",
        related_query_name="user",
    )
    
    def __str__(self):
        return self.username


# COUNTY MODEL
class County(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

    @property
    def total_wards(self):
        return self.wards.count()
    
    @property
    def total_localities(self):
        from core.models import Locality
        return Locality.objects.filter(ward__county=self).count()
    
    @property
    def total_agrotechs(self):
        from core.models import User
        return User.objects.filter(user_type='agro', locality__ward__county=self).distinct().count()
    
    @property
    def total_cigs(self):
        from core.models import CommonInterestGroup
        return CommonInterestGroup.objects.filter(locality__ward__county=self).count()
    
    @property
    def total_farmers(self):
        from core.models import Farmer
        return Farmer.objects.filter(user__in=User.objects.filter(user_type='farmer', locality__ward__county=self)).count()
    
    @property
    def total_farms(self):
        from core.models import Farm
        return Farm.objects.filter(locality__ward__county=self).count()


# WARD MODEL
class Ward(models.Model):
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='wards')
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
    @property
    def total_localities(self):
        return self.localities.count()
    
    @property
    def total_cigs(self):
        from core.models import CommonInterestGroup
        return sum(locality.cigs.count() for locality in self.localities.all())
    
    @property
    def total_farms(self):
        from core.models import Farm
        return sum(locality.farms.count() for locality in self.localities.all())
    
    @property
    def total_farmers(self):
        from core.models import Farmer
        return sum(locality.farmers.count() for locality in self.localities.all())


# LOCALITY MODEL
class Locality(models.Model):
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='localities')
    name = models.CharField(max_length=100)
    # Agro-technician in charge (optional one-to-one)
    agro_technician = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'user_type': 'agro'}, related_name='in_charge_locality')
    
    def __str__(self):
        return self.name
    
    @property
    def total_cigs(self):
        return self.cigs.count()
    
    @property
    def total_farms(self):
        return self.farms.count()
    
    @property
    def total_farmers(self):
        return self.farmers.count()


# COMMON INTEREST GROUP (CIG) MODEL
class CommonInterestGroup(models.Model):
    locality = models.ForeignKey(Locality, on_delete=models.CASCADE, related_name='cigs')
    produce_type = models.CharField(max_length=100)
    group_number = models.PositiveIntegerField(default=1)
    # New fields for CIG
    current_cycle = models.OneToOneField('AgriculturalCycle', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_cig')
    number_of_farms = models.PositiveIntegerField(default=0)
    unit_of_measure = models.CharField(max_length=50, default='kg')
    total_units_current_cycle = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_units_last_cycle = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.locality.name}_{self.produce_type}_CIG_{self.group_number}"


# AGRICULTURAL CYCLE MODEL
class AgriculturalCycle(models.Model):
    start_week = models.CharField(max_length=20)  # e.g., WK1_2025
    end_week = models.CharField(max_length=20)    # e.g., WK8_2025
    # One-to-one link with respective CIG
    cig = models.OneToOneField(CommonInterestGroup, on_delete=models.CASCADE, related_name='agri_cycle')
    # One-to-one link with the relevant FarmProduce of that type (optional)
    farm_produce = models.OneToOneField('FarmProduce', on_delete=models.SET_NULL, null=True, blank=True, related_name='cycle')
    # Name: auto-generated as "CIG name + Start week"
    name = models.CharField(max_length=100)
    
    def save(self, *args, **kwargs):
        self.name = f"{self.cig} {self.start_week}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


# FARM PRODUCE MODEL (Adjusted)
class FarmProduce(models.Model):
    farm = models.ForeignKey('Farm', on_delete=models.CASCADE, related_name='farm_produces')
    produce_type = models.CharField(max_length=100)
    total_units = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_of_measure = models.CharField(max_length=50, default='kg')
    # IMPORTANT: Link to CommonInterestGroup with related_name "farm_produces"
    cig = models.ForeignKey(
        'CommonInterestGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='farm_produces'
    )
    agricultural_cycle = models.ForeignKey(
        'AgriculturalCycle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='produces'
    )
    
    def __str__(self):
        return f"{self.farm.name} - {self.produce_type}"


# FARMER MODEL
class Farmer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return self.user.username
    
    @property
    def farm_count(self):
        return self.farms.count()
    
    @property
    def farms_list(self):
        return self.farms.all()
    
    @property
    def total_cigs(self):
        cig_ids = set()
        for farm in self.farms.all():
            for produce in farm.farm_produces.all():
                if produce.agricultural_cycle and produce.agricultural_cycle.cig:
                    cig_ids.add(produce.agricultural_cycle.cig.id)
        return len(cig_ids)
    
    @property
    def cigs_list(self):
        cig_set = set()
        for farm in self.farms.all():
            for produce in farm.farm_produces.all():
                if produce.agricultural_cycle and produce.agricultural_cycle.cig:
                    cig_set.add(produce.agricultural_cycle.cig)
        return list(cig_set)


# FARM MODEL
class Farm(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='farms')
    name = models.CharField(max_length=100)
    locality = models.ForeignKey(Locality, on_delete=models.SET_NULL, null=True, related_name='farms')
    # GPS coordinates
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # Many-to-many relationship to CIGs that the farm is registered to
    cigs = models.ManyToManyField(CommonInterestGroup, blank=True, related_name='farms_registered')
    
    def __str__(self):
        return self.name
    
    @property
    def farm_produce_types(self):
        return set(fp.produce_type for fp in self.farm_produces.all())
    
    @property
    def farm_produce_list(self):
        return self.farm_produces.all()