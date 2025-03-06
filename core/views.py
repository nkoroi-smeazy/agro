from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import County, Ward, Locality, CommonInterestGroup, Farmer, Farm, FarmProduce, User
from .serializers import (CountySerializer, WardSerializer, LocalitySerializer, 
                          CommonInterestGroupSerializer, FarmerSerializer, FarmSerializer, 
                          FarmProduceSerializer, UserSerializer)
from .permissions import IsAdminUserOrAgroTech, IsOwnerOrAdmin
from .utils import assign_to_cig  # (optional) for business logic

class CountyViewSet(viewsets.ModelViewSet):
    queryset = County.objects.all()
    serializer_class = CountySerializer
    permission_classes = [IsAuthenticated, IsAdminUserOrAgroTech]

class WardViewSet(viewsets.ModelViewSet):
    queryset = Ward.objects.all()
    serializer_class = WardSerializer
    permission_classes = [IsAuthenticated, IsAdminUserOrAgroTech]

class LocalityViewSet(viewsets.ModelViewSet):
    queryset = Locality.objects.all()
    serializer_class = LocalitySerializer
    permission_classes = [IsAuthenticated, IsAdminUserOrAgroTech]

class CommonInterestGroupViewSet(viewsets.ModelViewSet):
    queryset = CommonInterestGroup.objects.all()
    serializer_class = CommonInterestGroupSerializer
    permission_classes = [AllowAny]
    #permission_classes = [IsAuthenticated, IsAdminUserOrAgroTech]

class FarmerViewSet(viewsets.ModelViewSet):
    queryset = Farmer.objects.all()
    serializer_class = FarmerSerializer
    permission_classes = [AllowAny]
    #permission_classes = [IsAuthenticated, IsAdminUserOrAgroTech]  # Only Admin/Agro can create or update Farmer accounts

class FarmViewSet(viewsets.ModelViewSet):
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    permission_classes = [AllowAny]
    #permission_classes = [IsAuthenticated, IsOwnerOrAdmin]  # Owners (or Admin) can edit their farms

class FarmProduceViewSet(viewsets.ModelViewSet):
    queryset = FarmProduce.objects.all()
    serializer_class = FarmProduceSerializer
    permission_classes = [AllowAny]
    #permission_classes = [IsAuthenticated, IsOwnerOrAdmin]  # Only allow owners or Admin to modify

    def perform_create(self, serializer):
        instance = serializer.save()
        # Call business logic to automatically assign to a CIG based on produce type and locality.
        assign_to_cig(instance)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    #permission_classes = [IsAuthenticated, IsAdminUserOrAgroTech]  # Only Admin/Agro can manage user accounts
