from rest_framework import permissions, generics, serializers
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
)
from theatre.permissions import IsAdminOrIfAuthenticatedReadOnly


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


class PlayDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Play.objects.prefetch_related("genres", "actors", "reviews")
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]
    serializer_class = PlayDetailSerializer


class ActorListView(generics.ListCreateAPIView):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]


class ActorDetailView(generics.RetrieveDestroyAPIView):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]


class GenreListView(generics.ListCreateAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]


class GenreDetailView(generics.RetrieveDestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]


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


class ReviewListView(generics.ListCreateAPIView):
    queryset = Review.objects.select_related("user", "play")
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReservationListView(generics.ListCreateAPIView):
    queryset = Reservation.objects.select_related("user").prefetch_related("tickets")
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReservationDetailView(generics.RetrieveDestroyAPIView):
    queryset = Reservation.objects.select_related("user").prefetch_related("tickets")
    serializer_class = ReservationDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


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
