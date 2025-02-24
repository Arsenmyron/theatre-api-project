from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers

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


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ("id", "first_name", "last_name")


class ActorFullNameSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Actor
        fields = ("full_name",)

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name")


class PlaySerializer(serializers.ModelSerializer):
    actors = ActorSerializer(many=True)
    genres = GenreSerializer(many=True)

    class Meta:
        model = Play
        fields = ("id", "title", "rating", "description", "actors", "genres")


class PlayListSerializer(PlaySerializer):
    actors = ActorFullNameSerializer(many=True)
    genres = GenreSerializer(many=True)
    reviews = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Play
        fields = (
            "id",
            "title",
            "rating",
            "description",
            "actors",
            "genres",
            "reviews",
        )

    def get_reviews(self, obj):
        return obj.reviews.count()

    def get_description(self, obj):
        return obj.description[:50] + "..." if obj.description else ""


class PlayPostSerializer(PlaySerializer):
    actors = serializers.ListField(child=serializers.IntegerField())
    genres = serializers.ListField(child=serializers.IntegerField())

    def create(self, validated_data):
        actors_data = validated_data.pop("actors")
        genres_data = validated_data.pop("genres")

        play = Play.objects.create(**validated_data)

        play.actors.set(Actor.objects.filter(id__in=actors_data))
        play.genres.set(Genre.objects.filter(id__in=genres_data))

        return play


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())
    play = serializers.PrimaryKeyRelatedField(queryset=Play.objects.all())

    class Meta:
        model = Review
        fields = ("id", "play", "user", "rating", "text", "created_at")


class ReviewPlaySerializer(ReviewSerializer):
    class Meta:
        model = Review
        fields = ("id", "user", "rating", "text", "created_at")


class PlayDetailSerializer(serializers.ModelSerializer):
    actors = ActorFullNameSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    reviews = ReviewPlaySerializer(many=True, read_only=True)

    class Meta:
        model = Play
        fields = ("id", "title", "rating", "description", "actors", "genres", "reviews")


class TheatreHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = ("id", "name", "rows", "seats_in_row", "capacity")


class TheatreHallNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = ("name",)


class PlayTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ("title",)


class PerformanceSerializer(serializers.ModelSerializer):
    play = PlayTitleSerializer(read_only=True)
    theatre_hall = TheatreHallNameSerializer(read_only=True)

    class Meta:
        model = Performance
        fields = ("id", "play", "theatre_hall", "show_time")


class TicketSerializer(serializers.ModelSerializer):
    performance = serializers.PrimaryKeyRelatedField(
        queryset=Performance.objects.all(), required=True
    )

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance", "reservation")

    def validate(self, data):
        if Ticket.objects.filter(
            performance=data["performance"],
            row=data["row"],
            seat=data["seat"],
        ).exists():
            raise serializers.ValidationError("This place is already reserved")
        return data


class ReservationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())
    tickets = TicketSerializer(many=True)

    class Meta:
        model = Reservation
        fields = ("id", "user", "created_at", "tickets")

    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        user = self.context["request"].user

        with transaction.atomic():
            reservation = Reservation.objects.create(user=user)
            tickets = []
            for ticket_data in tickets_data:
                row = ticket_data["row"]
                seat = ticket_data["seat"]
                performance = ticket_data["performance"]
                if Ticket.objects.filter(
                    performance=performance, row=row, seat=seat
                ).exists():
                    raise serializers.ValidationError("This place is already reserved.")
                tickets.append(Ticket(reservation=reservation, **ticket_data))

            Ticket.objects.bulk_create(tickets)
            return reservation
