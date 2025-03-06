from rest_framework import viewsets
from core.models import (
    County, Ward, Locality, CommonInterestGroup, AgriculturalCycle,
    FarmProduce, Farmer, Farm
)
from core.serializers import (
    CountySerializer, WardSerializer, LocalitySerializer,
    CommonInterestGroupSerializer, AgriculturalCycleSerializer,
    FarmProduceSerializer, FarmerSerializer, FarmSerializer
)

class CountyViewSet(viewsets.ModelViewSet):
    queryset = County.objects.all()
    serializer_class = CountySerializer

class WardViewSet(viewsets.ModelViewSet):
    queryset = Ward.objects.all()
    serializer_class = WardSerializer

class LocalityViewSet(viewsets.ModelViewSet):
    queryset = Locality.objects.all()
    serializer_class = LocalitySerializer

class CigViewSet(viewsets.ModelViewSet):
    queryset = CommonInterestGroup.objects.all()
    serializer_class = CommonInterestGroupSerializer

class AgriculturalCycleViewSet(viewsets.ModelViewSet):
    queryset = AgriculturalCycle.objects.all()
    serializer_class = AgriculturalCycleSerializer

class FarmProduceViewSet(viewsets.ModelViewSet):
    queryset = FarmProduce.objects.all()
    serializer_class = FarmProduceSerializer

class FarmerViewSet(viewsets.ModelViewSet):
    queryset = Farmer.objects.all()
    serializer_class = FarmerSerializer

class FarmViewSet(viewsets.ModelViewSet):
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer