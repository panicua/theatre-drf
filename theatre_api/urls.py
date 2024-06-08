from django.urls import path, include
from rest_framework import routers

from theatre_api.views import (
    GenreViewSet,
    ActorViewSet,
    PlayViewSet,
    PerformanceViewSet,
    TheatreHallViewSet,
    ReservationViewSet,
)

app_name = "theatre_api"


router = routers.DefaultRouter()
router.register("genres", GenreViewSet)
router.register("actors", ActorViewSet)
router.register("plays", PlayViewSet)
router.register("performances", PerformanceViewSet)
router.register("theatre_halls", TheatreHallViewSet)
router.register("reservations", ReservationViewSet)

urlpatterns = [path("", include(router.urls))]
