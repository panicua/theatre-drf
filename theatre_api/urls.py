from django.urls import path, include
from rest_framework import routers

from theatre_api.views import (
    GenreViewSet,
    ActorViewSet, PlayViewSet, PerformanceViewSet,
)

app_name = "theatre_api"


router = routers.DefaultRouter()
router.register("genres", GenreViewSet)
router.register("actors", ActorViewSet)
router.register("plays", PlayViewSet)
router.register("performances", PerformanceViewSet)

urlpatterns = [path("", include(router.urls))]


