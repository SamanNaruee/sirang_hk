from rest_framework import serializers
from .models import Product, Farmer, Order


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price"]



class FarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmer
        fields = ["farmer_key", "token"]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["order_id", "status", "redirect_url", "created_at"]
        read_only_fields = ["order_id","redirect_url", "created_at"]

