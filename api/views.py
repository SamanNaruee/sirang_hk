from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from .models import Farmer
from rest_framework import status

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
            farmer_key=farmer_key, token=auth_token
        )
        data = {}
        data["farmer"] = farmer.__dict__ if created else 'None'
        data["response"] = response.json()

        return Response(data, status=status.HTTP_200_OK)


