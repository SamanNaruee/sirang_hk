from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
from .models import Farmer
from rest_framework import status
import requests


class GetHamrahTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        farmer_key = settings.FARMER_KEY 
        auth_token = settings.HAMRAH_AUTH_TOKEN 

        if not farmer_key or not auth_token:
            return Response({"error": "Missing credentials"}, status=status.HTTP_400_BAD_REQUEST)

        import requests

        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        data = {"farmer_key": str(farmer_key)}
        response = requests.post("https://core.hamrahkeshavarz.ir/api/third-party/token", json=data, headers=headers)
        if response.status_code != 200:
            return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)
        farmer, created = Farmer.objects.update_or_create(
            farmer_key=farmer_key, token=response.data['token'] # Fix this TODO
        )
        data = {}
        data["farmer"] = farmer.__dict__ if created else 'None'
        data["response"] = response.json()

        return Response(data, status=status.HTTP_200_OK)


class FarmerInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        farmer = Farmer.objects.last()
        if not farmer:
            return Response({"error": "Farmer token not found"}, status=400)

        headers = {"Authorization": f"Bearer {farmer.token}"}
        url = "https://core.hamrahkeshavarz.ir/api/third-party/farmer-info/"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return Response(response.json(), status=response.status_code)
        return Response({"error": "Failed to fetch farmer info"}, status=response.status_code)

