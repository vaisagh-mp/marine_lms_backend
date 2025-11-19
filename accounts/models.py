from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ShipType(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Position(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class User(AbstractUser, BaseModel):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True)
    ship_type = models.ForeignKey(ShipType, on_delete=models.SET_NULL, null=True, blank=True)

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('employee', 'Employee'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')

    def __str__(self):
        return f"{self.username} ({self.position} - {self.ship_type})"
