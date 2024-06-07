from datetime import datetime

from django.db.models import F, Count
from drf_spectacular.utils import extend_schema, OpenApiExample, \
    extend_schema_view, OpenApiParameter
from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.decorators import action as action_
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from theatre_api.models import Genre, Actor, Play, Performance, TheatreHall, \
    Reservation
from theatre_api.paginators import LargeResultsSetPagination
from theatre_api.permissions import IsAdminOrIfAuthenticatedReadOnly, \
    IsStaffToDelete
from theatre_api.serializers import GenreSerializer, ActorSerializer, \
    PlaySerializer, PlayListSerializer, PlayDetailSerializer, \
    PlayPosterSerializer, PerformanceSerializer, PerformanceListSerializer, \
    PerformanceDetailSerializer, TheatreHallSerializer, ReservationSerializer, \
    ReservationListSerializer, ReservationDetailSerializer


class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    pagination_class = LargeResultsSetPagination

    @extend_schema(
        operation_id="createGenre",
        description="Create a new genre with its name.",
        request=GenreSerializer,
        responses={201: GenreSerializer},
        examples=[
            OpenApiExample(
                "Create Genre Example",
                summary="An example of creating a new genre.",
                description="This example shows how to create a new genre with the required field. Name should ne unique.",
                value={
                    "name": "Sci-fi",
                }
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ActorViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    pagination_class = LargeResultsSetPagination

    @extend_schema(
        operation_id="createActor",
        description="Create a new actor with first name and last name.",
        request=ActorSerializer,
        responses={201: ActorSerializer},
        examples=[
            OpenApiExample(
                "Create Actor Example",
                summary="An example of creating a new actor.",
                description="This example shows how to create a new actor with the required fields.",
                value={
                    "first_name": "John",
                    "last_name": "Doe"
                }
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class TheatreHallViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


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

        if order == "DESC":
            queryset = queryset.order_by("-title")
        else:
            queryset = queryset.order_by("title")

        return queryset.distinct()

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


@extend_schema_view(
    list=extend_schema(
        methods=["GET"],
        description="Retrieve movies with specified filters",
        parameters=[
            OpenApiParameter(
                name="date",
                description="Filter performances by date (?date=2024-06-09)",
                required=False,
                type={"type": "string", "format": "date"},
            ),
            OpenApiParameter(
                name="play",
                description="Filter movies that contain particular play (?play=Romeo)",
                required=False,
                type={"type": "string"},
            ),
            OpenApiParameter(
                name="order",
                description="Order movies by show_time (?order=ASC; ?order=DESC)",
                required=False,
                type={"type": "string"},
            ),
        ],
    ),
)
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

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer

        if self.action == "retrieve":
            return PerformanceDetailSerializer

        return super().get_serializer_class()

    def get_queryset(self):
        """Retrieve Performances through filters and/or order them."""
        date = self.request.query_params.get("date")
        play_name = self.request.query_params.get("play")
        order = self.request.query_params.get("order")

        queryset = self.queryset

        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(show_time__date=date)

        if play_name:
            queryset = queryset.filter(play__title__icontains=play_name)

        if order == "ASC":
            queryset = self.queryset.order_by("show_time")
        elif order == "DESC":
            queryset = self.queryset.order_by("-show_time")

        return queryset.distinct()


class ReservationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    """
    Staff users see all reservations, regular users only see their own.
    Staff users can delete any reservation, regular users cannot delete any.
    """
    queryset = Reservation.objects.prefetch_related(
        "tickets__performance__play", "tickets__performance__theatre_hall"
    )
    serializer_class = ReservationSerializer
    permission_classes = (IsAuthenticated, IsStaffToDelete)

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        if self.action == "retrieve":
            return ReservationDetailSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
