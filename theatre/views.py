from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, serializers, permissions
from rest_framework.generics import UpdateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from theatre.models import (
    Actor,
    Genre,
    TheatreHall,
    Performance,
    Reservation,
    Review,
    Play,
)
from theatre.serializers import (
    ReviewSerializer,
    ActorSerializer,
    GenreSerializer,
    PerformanceSerializer,
    ReservationSerializer,
    PlayListSerializer,
    PlayPostSerializer,
    PlayDetailSerializer,
    TheatreHallSerializer,
    ReservationDetailSerializer,
    PlayImageSerializer,
)
from theatre.permissions import IsAdminOrIfAuthenticatedReadOnly


@extend_schema(
    summary="Update Play image",
    description="Allows to upload a new image for an existing play.",
    responses={200: PlayImageSerializer},
)
class PlayImageUpdateView(UpdateAPIView):
    queryset = Play.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = PlayImageSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return get_object_or_404(Play, pk=self.kwargs["pk"])


@extend_schema(
    summary="List and create plays",
    description="Getting a list of all plays and create a new one.",
    responses={
        200: PlayListSerializer,
        201: PlayPostSerializer,
    },
)
class PlayListView(generics.ListCreateAPIView):
    queryset = Play.objects.prefetch_related("genres", "actors")
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return PlayListSerializer
        elif self.request.method == "POST":
            return PlayPostSerializer

    def get_queryset(self):
        queryset = self.queryset

        title = self.request.query_params.get("title", None)
        if title:
            queryset = queryset.filter(title__icontains=title)

        genre_id = self.request.query_params.get("genre", None)
        if genre_id:
            queryset = queryset.filter(genres=genre_id)

        return queryset


@extend_schema(
    summary="Retrieve, update or delete play",
    description="Allows you to retrieve detailed information about a play, update it, or delete it.",
    responses={
        200: PlayDetailSerializer,
    },
)
class PlayDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Play.objects.prefetch_related("genres", "actors", "reviews")
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]
    serializer_class = PlayDetailSerializer


@extend_schema(
    summary="List and create actors",
    description="Get a list of all actors or create a new one.",
    responses={200: ActorSerializer, 201: ActorSerializer},
)
class ActorListView(generics.ListCreateAPIView):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]


@extend_schema(
    summary="Retrieve or delete actor",
    description="Get detailed information about an actor or delete it.",
    responses={200: ActorSerializer},
)
class ActorDetailView(generics.RetrieveDestroyAPIView):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]


@extend_schema(
    summary="List and create genres",
    description="Get a list of all genres or create a new genre.",
    responses={200: GenreSerializer, 201: GenreSerializer},
)
class GenreListView(generics.ListCreateAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]


@extend_schema(
    summary="Retrieve or delete genre",
    description="Get detailed information about a genre or delete it.",
    responses={200: GenreSerializer},
)
class GenreDetailView(generics.RetrieveDestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]


@extend_schema(
    summary="List performances",
    description="Get a list of performances with optional filters.",
    responses={200: PerformanceSerializer},
)
class PerformanceListView(generics.ListAPIView):
    queryset = Performance.objects.select_related(
        "play", "theatre_hall"
    ).prefetch_related("play__genres")

    serializer_class = PerformanceSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]

    def get_queryset(self):
        queryset = self.queryset

        title = self.request.query_params.get("title", None)
        if title:
            queryset = queryset.filter(play__title__icontains=title)

        genre_id = self.request.query_params.get("genre", None)
        if genre_id:
            queryset = queryset.filter(play__genres=genre_id)

        sort_by = self.request.query_params.get("sort_by", None)
        if sort_by == "date":
            queryset = queryset.order_by("show_time")
        elif sort_by == "-date":
            queryset = queryset.order_by("-show_time")

        return queryset


@extend_schema(
    summary="List and create reviews",
    description="Get a list of reviews for plays or create a new review.",
    responses={200: ReviewSerializer, 201: ReviewSerializer},
)
class ReviewListView(generics.ListCreateAPIView):
    queryset = Review.objects.select_related("user", "play")
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(
    summary="List and create reservations",
    description="Get a list of user reservations or create a new reservation.",
    responses={200: ReservationSerializer, 201: ReservationSerializer},
)
class ReservationListView(generics.ListCreateAPIView):
    queryset = Reservation.objects.select_related("user").prefetch_related("tickets")
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(
    summary="Retrieve or delete reservation",
    description="Get detailed information about a reservation or delete it.",
    responses={200: ReservationDetailSerializer},
)
class ReservationDetailView(generics.RetrieveDestroyAPIView):
    queryset = Reservation.objects.select_related("user").prefetch_related("tickets")
    serializer_class = ReservationDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


@extend_schema(
    summary="List and create theatre halls",
    description="Get a list of all theatre halls or create a new theatre hall.",
    responses={200: TheatreHallSerializer, 201: TheatreHallSerializer},
)
class TheatreHallListView(generics.ListCreateAPIView):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]

    def get_queryset(self):
        queryset = self.queryset

        name = self.request.query_params.get("name", None)
        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset

    def perform_create(self, serializer):
        name = serializer.validated_data["name"]
        rows = serializer.validated_data["rows"]
        seats_in_row = serializer.validated_data["seats_in_row"]

        theatre_hall, created = TheatreHall.objects.get_or_create(
            name=name, rows=rows, seats_in_row=seats_in_row
        )
        if not created:
            raise serializers.ValidationError("Theatre Hall already exists.")

        serializer.instance = theatre_hall
