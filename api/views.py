from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
from .models import Farmer, Product
from rest_framework import status
import requests


class GetHamrahTokenView(APIView):  
    permission_classes = [AllowAny]  

    def post(self, request):  
        farmer_key = settings.FARMER_KEY   
        auth_token = settings.HAMRAH_AUTH_TOKEN   

        if not farmer_key or not auth_token:  
            return Response({"error": "Missing credentials"}, status=status.HTTP_400_BAD_REQUEST)  

        headers = {  
            "Authorization": f"Bearer {auth_token}",  
            "Content-Type": "application/json"  
        }  
        data = {"farmer_key": str(farmer_key)}  
        response = requests.post("https://core.hamrahkeshavarz.ir/api/third-party/token", json=data, headers=headers)  

        if response.status_code != 200:  
            return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)  

        response_data = response.json()
        token = response_data.get('token')

        if not token:  
            return Response({"error": "Token not found in response"}, status=status.HTTP_400_BAD_REQUEST)

        settings.HALF_HOUR_LIFETIME_TOKEN = token  

        # Update or create the Farmer object  
        farmer, created = Farmer.objects.update_or_create(  
            farmer_key=farmer_key,  
            defaults={'token': token}
        )  

        data = {  
            "farmer": farmer.__dict__ if created else 'None',  
            "response": response_data  
        }  

        return Response(data, status=status.HTTP_200_OK)  


class FarmerInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        farmer = Farmer.objects.last()
        if not farmer:
            return Response({"error": "Farmer token not found"}, status=400)

        headers = {  
            "Authorization": f"Bearer {settings.HALF_HOUR_LIFETIME_TOKEN}",  
        }  
        url = "https://core.hamrahkeshavarz.ir/api/third-party/farmer-info/"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return Response(response.json(), status=response.status_code)
        return Response({"error": "Failed to fetch farmer info, may you must refresh farmer_key and half_hour_token... ."}, status=response.status_code)


class VendorItemsView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        items = request.data.get("items", [])
        if not items:
            return Response({"error": "Enter valid data."}, status=400)
        
        farmer = Farmer.objects.last()
        if not farmer or not farmer.token or not farmer.farmer_key:
            return Response({"error": "Farmer key not found"}, status=400)

        headers = {"Authorization": f"Bearer {settings.HALF_HOUR_LIFETIME_TOKEN}"}
        url = "https://core.hamrahkeshavarz.ir/api/third-party/vendor/items"
        response = requests.post(url, headers=headers, json=request.data)

        if response.status_code == 201:
            for item in request.data.get("items", []):
                Product.objects.update_or_create(id=item["id"], defaults={"name": item["name"], "price": item["price"]})
            return Response(response.json(), status=201)
        return Response({"error": "Failed to update items"}, status=response.status_code)
