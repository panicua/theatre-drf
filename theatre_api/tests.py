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
    return User.objects.create_superuser(
        email="admin@example.com", password="adminpassword"
    )


def create_user():
    return User.objects.create_user(
        email="user@example.com", password="userpassword"
    )


def get_token(email, password):
    client = APIClient()
    response = client.post(
        "/api/user/token/",
        {"email": email, "password": password},
    )
    return response.data["access"]


def get_user_token():
    return get_token("user@example.com", "userpassword")


def get_admin_token():
    return get_token("admin@example.com", "adminpassword")


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

    def test_unauthenticated_access(self):
        endpoints = [
            "/api/theatre/plays/",
            "/api/theatre/theatre_halls/",
            "/api/theatre/reservations/",
            "/api/theatre/performances/",
        ]
        client = APIClient()

        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = client.get(endpoint)
                self.assertEqual(response.status_code, 401)

        allowed_endpoints = [
            "/api/theatre/actors/",
            "/api/theatre/genres/",
        ]

        for endpoint in allowed_endpoints:
            with self.subTest(endpoint=endpoint):
                response = client.get(endpoint)
                self.assertEqual(response.status_code, 200)


class AuthenticatedTheatreApiPageAccessTests(TestCase):

    def setUp(self):
        self.user = create_user()
        self.token = get_user_token()

    def test_authenticated_access(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)
        endpoints = [
            "/api/theatre/plays/",
            "/api/theatre/theatre_halls/",
            "/api/theatre/reservations/",
            "/api/theatre/actors/",
            "/api/theatre/genres/",
            "/api/theatre/performances/",
        ]

        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = client.get(endpoint)
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

    def test_delete_operations(self):
        endpoints = [
            reverse("theatre_api:actor-detail", args=[self.actor.id]),
            reverse("theatre_api:genre-detail", args=[self.genre.id]),
            reverse("theatre_api:play-detail", args=[self.play.id]),
            reverse("theatre_api:theatre_halls-detail", args=[self.theatre_hall.id]),
            reverse("theatre_api:performance-detail", args=[self.performance.id]),
        ]

        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.delete(endpoint)
                self.assertEqual(response.status_code, 403)

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

    def test_delete_operations(self):
        endpoints = [
            reverse("theatre_api:actor-detail", args=[self.actor.id]),
            reverse("theatre_api:genre-detail", args=[self.genre.id]),
            reverse("theatre_api:play-detail", args=[self.play.id]),
            reverse("theatre_api:theatre_halls-detail", args=[self.theatre_hall.id]),
        ]

        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.delete(endpoint)
                print(f"Endpoint: {endpoint}, Status Code: {response.status_code}, Content: {response.content}")
                self.assertEqual(response.status_code, 204)

    def test_post_operations(self):
        post_data = {
            "actor": {"first_name": "John", "last_name": "Doe"},
            "genre": {"name": "Comedy"},
            "theatre_hall": {"name": "Main Hall", "rows": 10, "seats_in_row": 20},
            "play": {
                "title": "Hamlet",
                "description": "A Shakespearean tragedy",
                "genres": [self.genre.id],
                "actors": [self.actor.id]
            },
            "performance": {
                "play": self.play.id,
                "theatre_hall": self.theatre_hall.id,
                "show_time": datetime.datetime.now(),
            },
        }

        post_endpoints = {
            "actor": reverse("theatre_api:actor-list"),
            "genre": reverse("theatre_api:genre-list"),
            "theatre_hall": reverse("theatre_api:theatre_halls-list"),
            "play": reverse("theatre_api:play-list"),
            "performance": reverse("theatre_api:performance-list"),
        }

        for model, endpoint in post_endpoints.items():
            with self.subTest(model=model):
                response = self.client.post(endpoint, post_data[model], format="json")
                self.assertEqual(response.status_code, 201)
                created_id = response.data["id"]

                if model == "theatre_hall":
                    model = "theatre_halls"
                detail_endpoint = reverse(f"theatre_api:{model}-detail", args=[created_id])
                response = self.client.get(detail_endpoint)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data["id"], created_id)