from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CountyViewSet, WardViewSet, LocalityViewSet, CigViewSet,
    AgriculturalCycleViewSet, FarmProduceViewSet, FarmerViewSet, FarmViewSet
)

router = DefaultRouter()
router.register(r'counties', CountyViewSet)
router.register(r'wards', WardViewSet)
router.register(r'localities', LocalityViewSet)
router.register(r'cigs', CigViewSet)
router.register(r'agriculturalcycles', AgriculturalCycleViewSet)
router.register(r'produces', FarmProduceViewSet)
router.register(r'farmers', FarmerViewSet)
router.register(r'farms', FarmViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
