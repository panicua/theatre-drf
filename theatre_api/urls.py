from django.urls import path, include
from rest_framework import routers

from theatre_api.views import (
    GenreViewSet,
    ActorViewSet,
)

app_name = "theatre_api"


router = routers.DefaultRouter()
router.register("genres", GenreViewSet)
router.register("actors", ActorViewSet)

urlpatterns = [path("", include(router.urls))]


