from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Car, ServiceType, MaintenanceRequest, Review
from django.urls import reverse
from datetime import date, timedelta

class CarModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.car = Car.objects.create(owner=self.user, make="Toyota", model="Yaris", year=2020, vin="12345678901234567")

    def test_car_str(self):
        self.assertIn("Toyota Yaris", str(self.car))

class ServiceTypeTest(TestCase):
    def test_create_service(self):
        s = ServiceType.objects.create(name="Oil Change", category="Basic Maintenance")
        self.assertEqual(s.name, "Oil Change")

class MaintenanceRequestTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser2', 'test2@example.com', 'password')
        self.car = Car.objects.create(owner=self.user, make="Honda", model="Civic", year=2021, vin="12345678901234568")
        self.service = ServiceType.objects.create(name="Tune Up", category="Performance", hp_gain=10)

    def test_request_creation(self):
        req = MaintenanceRequest.objects.create(car=self.car, service=self.service, requested_date=date.today())
        self.assertEqual(req.car, self.car)
        self.assertEqual(req.service, self.service)

class CarViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser3', 'test3@example.com', 'password')
        self.client.login(username='testuser3', password='password')

    def test_car_list_view(self):
        url = reverse('car-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_add_car(self):
        url = reverse('car-add')
        data = {
            'make': 'Ford',
            'model': 'Focus',
            'year': 2022,
            'vin': '12345678901234569',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after success

class RegisterLoginTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_page(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_login_logout(self):
        User.objects.create_user('testuser4', 'test4@example.com', 'password')
        login = self.client.login(username='testuser4', password='password')
        self.assertTrue(login)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        response = self.client.get(reverse('dashboard'))
        self.assertNotEqual(response.status_code, 200)  # Should redirect to login

class MaintenanceRequestFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser5', 'test5@example.com', 'password')
        self.car = Car.objects.create(owner=self.user, make="BMW", model="320", year=2019, vin="12345678901234570")

    def test_form_invalid_past_date(self):
        from .forms import MaintenanceRequestForm
        form = MaintenanceRequestForm(data={
            'car': self.car.pk,
            'requested_date': date.today() - timedelta(days=1),
            'notes': 'test'
        }, user=self.user)
        self.assertFalse(form.is_valid())

class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('reviewer', 'review@example.com', 'password')
        self.car = Car.objects.create(owner=self.user, make="VW", model="Golf", year=2021, vin="12345678901234571")
        self.service = ServiceType.objects.create(name="Wax", category="Aesthetic")
        self.req = MaintenanceRequest.objects.create(car=self.car, service=self.service, requested_date=date.today())
        self.review = Review.objects.create(user=self.user, request=self.req, rating=5, comment="Great!")

    def test_review_str(self):
        self.assertIn("Great!", self.review.comment)


