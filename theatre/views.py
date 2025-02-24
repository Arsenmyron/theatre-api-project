from django.shortcuts import get_object_or_404

from rest_framework import status, permissions, generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from theatre.models import (
    Actor,
    Genre,
    TheatreHall,
    Performance,
    Reservation,
    Ticket,
    Review,
    Play,
)
from theatre.serializers import (
    PlaySerializer,
    ReviewSerializer,
    ActorSerializer,
    GenreSerializer,
    PerformanceSerializer,
    ReservationSerializer,
    TicketSerializer,
    PlayListSerializer,
    PlayPostSerializer,
    PlayDetailSerializer,
    TheatreHallSerializer,
)


class PlayListView(generics.ListCreateAPIView):
    queryset = Play.objects.prefetch_related("genres", "actors")
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return PlayListSerializer
        elif self.request.method == "POST":
            return PlayPostSerializer


class PlayDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Play.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = PlayDetailSerializer


class ActorListView(generics.ListCreateAPIView):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = [permissions.AllowAny]


class GenreListView(generics.ListCreateAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.AllowAny]


class PerformanceListView(generics.ListAPIView):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer
    permission_classes = [permissions.AllowAny]


class ReviewListView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

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
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class TheatreHallListView(generics.ListCreateAPIView):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer

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
