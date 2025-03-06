from rest_framework import serializers
from .models import County, Ward, Locality, CommonInterestGroup, Farmer, Farm, FarmProduce, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_type']

class CountySerializer(serializers.ModelSerializer):
    class Meta:
        model = County
        fields = '__all__'

class WardSerializer(serializers.ModelSerializer):
    county = CountySerializer(read_only=True)
    county_id = serializers.PrimaryKeyRelatedField(queryset=County.objects.all(), source='county', write_only=True)
    class Meta:
        model = Ward
        fields = ['id', 'name', 'county', 'county_id']

class LocalitySerializer(serializers.ModelSerializer):
    ward = WardSerializer(read_only=True)
    ward_id = serializers.PrimaryKeyRelatedField(queryset=Ward.objects.all(), source='ward', write_only=True)
    class Meta:
        model = Locality
        fields = ['id', 'name', 'ward', 'ward_id']

class CommonInterestGroupSerializer(serializers.ModelSerializer):
    locality = LocalitySerializer(read_only=True)
    locality_id = serializers.PrimaryKeyRelatedField(queryset=Locality.objects.all(), source='locality', write_only=True)
    class Meta:
        model = CommonInterestGroup
        fields = ['id', 'produce_type', 'group_number', 'locality', 'locality_id']

class FarmerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Farmer
        fields = ['id', 'user', 'contact_number']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        farmer = Farmer.objects.create(user=user, **validated_data)
        return farmer

class FarmSerializer(serializers.ModelSerializer):
    farmer = FarmerSerializer(read_only=True)
    farmer_id = serializers.PrimaryKeyRelatedField(queryset=Farmer.objects.all(), source='farmer', write_only=True)
    locality = LocalitySerializer(read_only=True)
    locality_id = serializers.PrimaryKeyRelatedField(queryset=Locality.objects.all(), source='locality', write_only=True)
    class Meta:
        model = Farm
        fields = ['id', 'name', 'farmer', 'farmer_id', 'locality', 'locality_id']

class FarmProduceSerializer(serializers.ModelSerializer):
    farm = FarmSerializer(read_only=True)
    farm_id = serializers.PrimaryKeyRelatedField(queryset=Farm.objects.all(), source='farm', write_only=True)
    cig = CommonInterestGroupSerializer(read_only=True)
    cig_id = serializers.PrimaryKeyRelatedField(queryset=CommonInterestGroup.objects.all(), source='cig', write_only=True, required=False, allow_null=True)
    class Meta:
        model = FarmProduce
        fields = ['id', 'produce_type', 'quantity', 'farm', 'farm_id', 'cig', 'cig_id']
