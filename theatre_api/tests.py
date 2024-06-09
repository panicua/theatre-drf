import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from theatre_api.models import (
    Actor,
    Genre,
    Play,
    TheatreHall,
    Performance,
)

User = get_user_model()


def create_admin_user():
    user = User.objects.create_superuser(
        email="admin@example.com", password="adminpassword"
    )
    return user


def create_user():
    user = User.objects.create_user(
        email="user@example.com", password="userpassword"
    )
    return user


def get_user_token():
    client = APIClient()
    response = client.post(
        "/api/user/token/",
        {"email": "user@example.com", "password": "userpassword"},
    )
    return response.data["access"]


def get_admin_token():
    client = APIClient()
    response = client.post(
        "/api/user/token/",
        {"email": "admin@example.com", "password": "adminpassword"},
    )
    return response.data["access"]


def setup_common_data(user_token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Bearer " + user_token)
    actor = Actor.objects.create(first_name="John", last_name="Doe")
    genre = Genre.objects.create(name="Drama")
    theatre_hall = TheatreHall.objects.create(
        name="Theatre Hall", rows=10, seats_in_row=11
    )
    play = Play.objects.create(
        title="The Godfather",
        description="The story of the Corleone family.",
    )
    play.genres.add(genre)
    play.actors.add(actor)
    performance = Performance.objects.create(
        play=play,
        theatre_hall=theatre_hall,
        show_time=datetime.datetime.now(),
    )
    reservation_data = {
        "tickets": [
            {
                "row": 1,
                "seat": 1,
                "performance": performance.id,
            }
        ]
    }
    return (
        client,
        actor,
        genre,
        theatre_hall,
        play,
        performance,
        reservation_data,
    )


class UnauthenticatedTheatreApiPageAccessTests(TestCase):

    def test_unauthenticated_plays_api(self):
        client = APIClient()
        response = client.get("/api/theatre/plays/")
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_theatre_halls_api(self):
        client = APIClient()
        response = client.get("/api/theatre/theatre_halls/")
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_reservations_api(self):
        client = APIClient()
        response = client.get("/api/theatre/reservations/")
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_actors_api(self):
        client = APIClient()
        response = client.get("/api/theatre/actors/")
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_genres_api(self):
        client = APIClient()
        response = client.get("/api/theatre/genres/")
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_performances_api(self):
        client = APIClient()
        response = client.get("/api/theatre/performances/")
        self.assertEqual(response.status_code, 401)


class AuthenticatedTheatreApiPageAccessTests(TestCase):

    def setUp(self):
        self.user = create_user()
        self.token = get_user_token()

    def test_authenticated_plays_api(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)
        response = client.get("/api/theatre/plays/")
        self.assertEqual(response.status_code, 200)

    def test_authenticated_theatre_halls_api(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)
        response = client.get("/api/theatre/theatre_halls/")
        self.assertEqual(response.status_code, 200)

    def test_authenticated_reservations_api(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)
        response = client.get("/api/theatre/reservations/")
        self.assertEqual(response.status_code, 200)

    def test_authenticated_actors_api(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)
        response = client.get("/api/theatre/actors/")
        self.assertEqual(response.status_code, 200)

    def test_authenticated_genres_api(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)
        response = client.get("/api/theatre/genres/")
        self.assertEqual(response.status_code, 200)

    def test_authenticated_performances_api(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)
        response = client.get("/api/theatre/performances/")
        self.assertEqual(response.status_code, 200)


class AuthenticatedNotStaffTheatreApiDeleteTests(TestCase):

    def setUp(self):
        self.user = create_user()
        self.token = get_user_token()
        (
            self.client,
            self.actor,
            self.genre,
            self.theatre_hall,
            self.play,
            self.performance,
            self.reservation_data,
        ) = setup_common_data(self.token)

    def test_delete_actor(self):
        response = self.client.delete(
            reverse("theatre_api:actor-detail", args=[self.actor.id])
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_genre(self):
        response = self.client.delete(
            reverse("theatre_api:genre-detail", args=[self.genre.id])
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_play(self):
        response = self.client.delete(
            reverse("theatre_api:play-detail", args=[self.play.id])
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_theatre_hall(self):
        response = self.client.delete(
            reverse(
                "theatre_api:theatre_halls-detail", args=[self.theatre_hall.id]
            )
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_performance(self):
        response = self.client.delete(
            reverse(
                "theatre_api:performance-detail", args=[self.performance.id]
            )
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_reservation(self):
        response = self.client.post(
            reverse("theatre_api:reservation-list"),
            self.reservation_data,
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        reservation_id = response.data["id"]

        response = self.client.delete(
            reverse("theatre_api:reservation-detail", args=[reservation_id])
        )
        self.assertEqual(response.status_code, 403)


class StaffTheatreApiDeleteTests(TestCase):

    def setUp(self):
        self.user = create_admin_user()
        self.token = get_admin_token()
        (
            self.client,
            self.actor,
            self.genre,
            self.theatre_hall,
            self.play,
            self.performance,
            self.reservation_data,
        ) = setup_common_data(self.token)

    def test_delete_actor(self):
        response = self.client.delete(
            reverse("theatre_api:actor-detail", args=[self.actor.id])
        )
        self.assertEqual(response.status_code, 204)

    def test_delete_genre(self):
        response = self.client.delete(
            reverse("theatre_api:genre-detail", args=[self.genre.id])
        )
        self.assertEqual(response.status_code, 204)

    def test_delete_play(self):
        response = self.client.delete(
            reverse("theatre_api:play-detail", args=[self.play.id])
        )
        self.assertEqual(response.status_code, 204)

    def test_delete_theatre_hall(self):
        response = self.client.delete(
            reverse(
                "theatre_api:theatre_halls-detail", args=[self.theatre_hall.id]
            )
        )
        self.assertEqual(response.status_code, 204)

    def test_delete_performance(self):
        response = self.client.delete(
            reverse(
                "theatre_api:performance-detail", args=[self.performance.id]
            )
        )
        self.assertEqual(response.status_code, 204)

    def test_delete_reservation(self):
        response = self.client.post(
            reverse("theatre_api:reservation-list"),
            self.reservation_data,
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        reservation_id = response.data["id"]

        response = self.client.delete(
            reverse("theatre_api:reservation-detail", args=[reservation_id])
        )
        self.assertEqual(response.status_code, 204)
