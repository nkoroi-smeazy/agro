from rest_framework import serializers
from core.models import (
    User, County, Ward, Locality, CommonInterestGroup, AgriculturalCycle,
    FarmProduce, Farmer, Farm
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_type', 'locality']

class CountySerializer(serializers.ModelSerializer):
    total_wards = serializers.IntegerField(read_only=True)
    total_localities = serializers.IntegerField(read_only=True)
    total_agrotechs = serializers.IntegerField(read_only=True)
    total_cigs = serializers.IntegerField(read_only=True)
    total_farmers = serializers.IntegerField(read_only=True)
    total_farms = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = County
        fields = '__all__'

class WardSerializer(serializers.ModelSerializer):
    total_localities = serializers.IntegerField(read_only=True)
    total_cigs = serializers.IntegerField(read_only=True)
    total_farms = serializers.IntegerField(read_only=True)
    total_farmers = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Ward
        fields = '__all__'

class LocalitySerializer(serializers.ModelSerializer):
    total_cigs = serializers.IntegerField(read_only=True)
    total_farms = serializers.IntegerField(read_only=True)
    total_farmers = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Locality
        fields = '__all__'

class AgriculturalCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgriculturalCycle
        fields = '__all__'

class CommonInterestGroupSerializer(serializers.ModelSerializer):
    current_cycle = AgriculturalCycleSerializer(read_only=True)
    
    class Meta:
        model = CommonInterestGroup
        fields = '__all__'

class FarmProduceSerializer(serializers.ModelSerializer):
    agricultural_cycle = AgriculturalCycleSerializer(read_only=True)
    
    class Meta:
        model = FarmProduce
        fields = '__all__'

class FarmerSerializer(serializers.ModelSerializer):
    farm_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Farmer
        fields = '__all__'

class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = '__all__'