from django.db.models import F, Count
from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.decorators import action as action_
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from theatre_api.models import Genre, Actor, Play, Performance
from theatre_api.paginators import LargeResultsSetPagination
from theatre_api.permissions import IsAdminOrIfAuthenticatedReadOnly
from theatre_api.serializers import GenreSerializer, ActorSerializer, \
    PlaySerializer, PlayListSerializer, PlayDetailSerializer, \
    PlayPosterSerializer, PerformanceSerializer


class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    pagination_class = LargeResultsSetPagination


class ActorViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    pagination_class = LargeResultsSetPagination


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.prefetch_related("genres", "actors")
    serializer_class = PlaySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @staticmethod
    def _split_params_str_to_words(string_) -> list:
        return [word for word in string_.split(",") if word]

    def get_queryset(self):
        """Retrieve Plays through filters and/or order them."""
        title = self.request.query_params.get("title", None)
        genre = self.request.query_params.get("genre", None)
        actor = self.request.query_params.get("actor", None)

        order = self.request.query_params.get("order", None)

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)

        if genre:
            genres = self._split_params_str_to_words(genre)
            for genre in genres:
                queryset = queryset.filter(genres__name__icontains=genre)

        if actor:
            actors = self._split_params_str_to_words(actor)
            for actor in actors:
                queryset = queryset.filter(
                    actors__last_name__icontains=actor
                ) or queryset.filter(
                    actors__first_name__icontains=actor
                )

        if order == "title":
            queryset = queryset.order_by("title")
        elif order == "-title":
            queryset = queryset.order_by("-title")

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer

        elif self.action == "retrieve":
            return PlayDetailSerializer

        return super().get_serializer_class()

    @action_(
        methods=["POST"],
        detail=True,
        permission_classes=[IsAdminUser],
        url_path="upload-image",
        serializer_class=PlayPosterSerializer
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to the specific Play"""
        play = self.get_object()
        serializer = self.get_serializer(play, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = (
        Performance.objects
        .select_related("play", "theatre_hall")
        .annotate(
            tickets_available=(
                    F("theatre_hall__rows") * F("theatre_hall__seats_in_row")
                    - Count("tickets")
            )
        )
    )
    serializer_class = PerformanceSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
