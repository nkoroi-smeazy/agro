from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CountyViewSet, WardViewSet, LocalityViewSet, 
                    CommonInterestGroupViewSet, FarmerViewSet, FarmViewSet, 
                    FarmProduceViewSet, UserViewSet)

router = DefaultRouter()
router.register(r'counties', CountyViewSet)
router.register(r'wards', WardViewSet)
router.register(r'localities', LocalityViewSet)
router.register(r'cigs', CommonInterestGroupViewSet)
router.register(r'farmers', FarmerViewSet)
router.register(r'farms', FarmViewSet)
router.register(r'produces', FarmProduceViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
