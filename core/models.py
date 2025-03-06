from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Custom User model with role differentiation
USER_TYPE_CHOICES = (
    ('admin', 'Admin'),
    ('farmer', 'Farmer'),
    ('agro', 'Agro-Technician'),
)

class User(AbstractUser):
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    
    # Override groups and user_permissions with custom related names to avoid clashes.
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

# Geographical hierarchy
class County(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Ward(models.Model):
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='wards')
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Locality(models.Model):
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='localities')
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

# Common Interest Group (CIG)
class CommonInterestGroup(models.Model):
    locality = models.ForeignKey(Locality, on_delete=models.CASCADE, related_name='cigs')
    produce_type = models.CharField(max_length=100)
    group_number = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.locality.name}_{self.produce_type}_CIG_{self.group_number}"

# Farmer profile (only created by Agro-Technicians)
class Farmer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    def __str__(self):
        return self.user.username

# Farm model, owned by a Farmer and located in a Locality
class Farm(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='farms')
    name = models.CharField(max_length=100)
    locality = models.ForeignKey(Locality, on_delete=models.SET_NULL, null=True, related_name='farms')
    def __str__(self):
        return self.name

# FarmProduce: links a Farm with a produce type and its CIG
class FarmProduce(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='produces')
    produce_type = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)
    cig = models.ForeignKey(CommonInterestGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='farm_produces')
    
    def __str__(self):
        return f"{self.farm.name} - {self.produce_type}"
