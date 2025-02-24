from django.urls import path

from theatre.views import (
    ActorListView,
    GenreListView,
    PlayListView,
    PerformanceListView,
    ReviewListView,
    ReservationListView,
    ReservationDetailView,
    PlayDetailView,
    TheatreHallListView,
)

urlpatterns = [
    path("actors/", ActorListView.as_view(), name="actor-list"),
    path("genres/", GenreListView.as_view(), name="genre-list"),
    path("plays/", PlayListView.as_view(), name="play-list"),
    path("plays/<int:pk>/", PlayDetailView.as_view(), name="play-detail"),
    path("performances/", PerformanceListView.as_view(), name="performance-list"),
    path("reviews/", ReviewListView.as_view(), name="review-list"),
    path("reservations/", ReservationListView.as_view(), name="reservation-list"),
    path(
        "reservations/<int:pk>/",
        ReservationDetailView.as_view(),
        name="reservation-detail",
    ),
    path("theatre-halls/", TheatreHallListView.as_view(), name="theatre-hall-list"),
]
