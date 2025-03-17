from django.db import models
import uuid

class Farmer(models.Model):
    farmer_key = models.UUIDField(primary_key=True, editable=False, unique=True)
    token = models.UUIDField(max_length=1024)
    created_at = models.DateTimeField(auto_now_add=True)
