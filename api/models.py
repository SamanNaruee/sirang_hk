from django.db import models
import uuid

class Farmer(models.Model):
    farmer_key = models.UUIDField(primary_key=True, editable=False, unique=True)
    token = models.UUIDField(max_length=1024)
    created_at = models.DateTimeField(auto_now_add=True)

class Product(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    price = models.PositiveIntegerField()

class Order(models.Model):
    order_id = models.UUIDField(primary_key=True)
    status = models.CharField(max_length=50)
    redirect_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

class HalfHourToken(models.Model):
    token = models.CharField(max_length=1024, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)