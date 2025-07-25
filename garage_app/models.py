from django.db import models
from django.contrib.auth.models import User

class ServiceType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    hp_gain = models.PositiveIntegerField(default=0, help_text="Horsepower gain from this service")
    CATEGORY_CHOICES = [
        ('Basic', 'Basic Maintenance'),
        ('Performance', 'Performance Upgrade'),
        ('Tuning', 'Custom Tuning'),
        ('Aesthetic', 'Aesthetic Mod'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='basic')

    def __str__(self):
        return self.name

class Car(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    vin = models.CharField(max_length=17, unique=True)
    image = models.ImageField(upload_to='car_images/', blank=True, null=True)  # ← NEW
    horsepower = models.PositiveIntegerField(blank=True, null=True)
    upgrades = models.TextField(blank=True)  # ← NEW FIELD



    def __str__(self):
        return f"{self.make} {self.model} ({self.vin})"

class MaintenanceRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    service = models.ForeignKey(ServiceType, on_delete=models.SET_NULL, null=True)
    requested_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    is_approved = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.car} - {self.service}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    request = models.ForeignKey('MaintenanceRequest', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, f"{i} Stars") for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.rating}★ for {self.request}"