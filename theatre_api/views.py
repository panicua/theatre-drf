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


@extend_schema_view(
    list=extend_schema(
        operation_id="listTheatreHalls",
        description="Retrieve a list of theatre halls with optional filtering by name.",
        parameters=[
            OpenApiParameter(
                name="name",
                description="Filter theatre halls by name (?name=Rome)",
                required=False,
                type={"type": "string"},
            ),
        ],
        responses={200: TheatreHallSerializer(many=True)},
        examples=[
            OpenApiExample(
                "List Theatre Halls Example",
                summary="An example of listing theatre halls with optional name filtering.",
                description="This example shows how to retrieve a list of theatre halls, optionally filtering by the name 'Main'.",
                value=[
                    {"id": 1, "name": "Main Hall", "rows": 10, "seats_in_row": 20, "capacity": 200},
                    {"id": 2, "name": "Small Hall", "rows": 5, "seats_in_row": 15, "capacity": 75},
                ]
            )
        ]
    ),
    create=extend_schema(
        operation_id="createTheatreHall",
        description="Create a new theatre hall with name, rows, and seats_in_row.",
        request=TheatreHallSerializer,
        responses={201: TheatreHallSerializer},
        examples=[
            OpenApiExample(
                "Create Theatre Hall Example",
                summary="An example of creating a new theatre hall.",
                description="This example shows how to create a new theatre hall with the required fields.",
                value={
                    "name": "Main Hall",
                    "rows": 10,
                    "seats_in_row": 20
                }
            )
        ]
    ),
)
class TheatreHallViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        name = self.request.query_params.get("name")

        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset


@extend_schema_view(
    list=extend_schema(
        methods=["GET"],
        description="Retrieve plays with specified filters",
        parameters=[
            OpenApiParameter(
                name="title",
                description="Filter plays by title (?title=Inception)",
                required=False,
                type={"type": "string"},
            ),
            OpenApiParameter(
                name="genre",
                description="Filter plays by genre (?genre=drama,action)",
                required=False,
                type={"type": "string"},
            ),
            OpenApiParameter(
                name="actor",
                description="Filter movies by actors (?actor=jolie,depp)",
                required=False,
                type={"type": "string"},
            ),
        ],
    ),
    create=extend_schema(
        methods=["POST"],
        description="Create a new play with title, description, genre, and actors",
        request=PlaySerializer,
        responses={201: PlaySerializer},
        examples=[
            OpenApiExample(
                "Create Play Example",
                summary="An example of creating a new play.",
                description="This example shows how to create a new play with the required fields. (genres and actors are ids/pks)",
                value={
                    "title": "Some Title",
                    "description": "Very interesting description",
                    "genres": [1, 2],
                    "actors": [2, 3]
                }
            )
        ]
    ),
)
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
        genres = self.request.query_params.get("genres", None)
        actors = self.request.query_params.get("actors", None)

        order = self.request.query_params.get("order", None)

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)

        if genres:
            genres = self._split_params_str_to_words(genres)
            for genre in genres:
                queryset = queryset.filter(genres__name__icontains=genre)

        if actors:
            actors = self._split_params_str_to_words(actors)
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
        description="Retrieve performances with specified filters",
        parameters=[
            OpenApiParameter(
                name="date",
                description="Filter performances by date (?date=2024-06-09)",
                required=False,
                type={"type": "string", "format": "date"},
            ),
            OpenApiParameter(
                name="play",
                description="Filter movies that contain particular play name (?play=Romeo)",
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
    create=extend_schema(
        methods=["POST"],
        description="Create a new performance with show_time, play and theatre_hall",
        request=PerformanceSerializer,
        responses={201: PerformanceSerializer},
        examples=[
            OpenApiExample(
                "Create a performance example",
                summary="An example of creating a new performance.",
                description="This example shows how to create a new performance with the required fields.",
                value={
                    "show_time": "2024-06-09 13:00:00",
                    "play": 2,
                    "theatre_hall": 1
                }
            )
        ]
    )
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


@extend_schema_view(
    list=extend_schema(
        methods=["GET"],
        description="Retrieve your reservations or filter by user id if staff member",
        parameters=[
            OpenApiParameter(
                name="user",
                description="Filter reservations by user id (?user=1)",
                required=False,
                type={"type": "string", "format": "number"},
            ),
        ],
    ),
    create=extend_schema(
        methods=["POST"],
        description="Create a new reservation with tickets info specified.",
        request=ReservationSerializer,
        responses={201: ReservationSerializer},
        examples=[
            OpenApiExample(
                "Create a reservation example",
                summary="An example of creating a new reservation.",
                description="This example shows how to create a new reservation with the required fields.",
                value={
                    "tickets": [
                        {"row": 1, "seat": 1, "performance": 1},
                        {"row": 1, "seat": 2, "performance": 1},
                    ]
                }
            )
        ]
    ),
    destroy=extend_schema(
        methods=["DELETE"],
        description="Delete reservation by id. Staff users can delete any reservation, regular users cannot delete any.",
    )
)
class ReservationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
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
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = self.queryset

        if self.request.user.is_staff:
            user = self.request.query_params.get("user")

            if user:
                queryset = queryset.filter(user=user)

            return queryset.distinct()
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
