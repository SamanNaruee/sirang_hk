from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
from .models import Farmer, Product, Order, HalfHourToken
from rest_framework import status
from .serializers import ProductSerializer, FarmerSerializer, OrderSerializer
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
        response = requests.post("https://core.hamrahkeshavarz.ir/api/third-party/token", json=data, headers=headers, timeout=10)  

        if response.status_code != 200:  
            return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)  

        response_data = response.json()
        token = response_data.get('token')

        if not token:  
            return Response({"error": "Token not found in response"}, status=status.HTTP_400_BAD_REQUEST)


        # Update or create the HalfHourToken object
        HalfHourToken.objects.update_or_create(
            token=token
        )

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


class FarmerUserInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        farmer = Farmer.objects.order_by('-created_at').first()
        if not farmer:
            return Response({"error": "Farmer token not found"}, status=400)

        HFT = HalfHourToken.objects.filter('-created_at').first()
        headers = {  
            "Authorization": f"Bearer {HFT.token}",  
        }  
        url = "https://core.hamrahkeshavarz.ir/api/third-party/farmer-info/"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return Response(response.json(), status=response.status_code)
        return Response({"error": "Failed to fetch farmer info, may you must refresh farmer_key and half_hour_token... ."}, status=response.status_code)


class VendorItemsView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        items = request.data.get("items", [])
        if not items:
            return Response({"error": "Enter valid data."}, status=400)
        
        farmer = Farmer.objects.order_by('-created_at').first()
        if not farmer or not farmer.token or not farmer.farmer_key:
            return Response({"error": "Farmer key not found"}, status=400)

        HFT = HalfHourToken.objects.filter('-created_at').first()
        headers = {"Authorization": f"Bearer {HFT.token}"}
        url = "https://core.hamrahkeshavarz.ir/api/third-party/vendor/items"
        response = requests.post(url, headers=headers, json=request.data, timeout=10)

        if response.status_code == 201:
            for item in request.data.get("items", []):
                Product.objects.update_or_create(id=item["id"], defaults={"name": item["name"], "price": item["price"]})
            return Response(response.json(), status=201)
        return Response({"error": "Failed to update items"}, status=response.status_code)


class OrderCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        farmer = Farmer.objects.order_by('-created_at').first()
        if not farmer or not farmer.token or not farmer.farmer_key:
            return Response({"error": "Farmer key not found"}, status=400)
        # request.data['items'] validation:
        items = request.data.get("items", [])
        if not items:
            return Response({"error": "Enter valid data."}, status=400)
        for item in items:
            if not item or not item['count'] or item['count'] <= 0:
                return Response({"error": "Enter valid data. it must be a list of dict with count > 0"}, status=400)
        
        HFT = HalfHourToken.objects.filter('-created_at').first()
        headers = {"Authorization": f"Bearer {HFT.token}"}
        url = "https://core.hamrahkeshavarz.ir/api/third-party/orders"
        response = requests.post(url, headers=headers, json=request.data, timeout=10)

        if response.status_code == 201:
            data = response.json()
            Order.objects.create(order_id=data["order_id"], redirect_url=data["redirect_url"], status="ON_PROCESSING")
            return Response(data, status=201)
        return Response({"error": "Failed to create order"}, status=response.status_code)

class ProductsView(APIView):  
    permission_classes = [AllowAny] 

    def get(self, request):  
        products = Product.objects.all()  
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=200)  
    
    def post(self, request):  
        serializer = ProductSerializer(data=request.data) 
        if serializer.is_valid(raise_exception=True):  
            product = serializer.save()
            return Response(ProductSerializer(product).data, status=201) 

class ProductDeleteView(APIView):  
    permission_classes = [AllowAny]

    def get(self, request, product_id):  
        try:
            product = Product.objects.get(id=product_id)
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=200)
        except Product.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)

    def delete(self, request, product_id):  
        try:
            product = Product.objects.get(id=product_id)
            product.delete()
            return Response({"detail": "Deleted successfully."}, status=204)
        except Product.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)


class OrderStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, order_id=None):
        if order_id:
            try:
                order = Order.objects.get(order_id=order_id)
            
            except Order.DoesNotExist:
                return Response({"error": "Order not found"}, status=404)
            HFT = HalfHourToken.objects.filter('-created_at').first()
            headers = {"Authorization": f"Bearer {HFT.token}"}
            url = f"https://core.hamrahkeshavarz.ir/api/third-party/orders/{order_id}"
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                order.status = data["status"]
                order.save()
                return Response(data, status=200)
            return Response({"error": "Failed to fetch order status"}, status=response.status_code)
        
        orders = Order.objects.all()
        orders = OrderSerializer(orders, many=True)
        return Response(orders.data, status=200)


class OrderConfirmView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, order_id=None):
        if order_id:
            try:
                order = Order.objects.get(order_id=order_id)
            except Order.DoesNotExist:
                return Response({"error": "Order not found"}, status=404)
            

            HFT = HalfHourToken.objects.filter('-created_at').first()
            headers = {"Authorization": f"Bearer {HFT.token}"}
            url = f"https://core.hamrahkeshavarz.ir/api/third-party/orders/{order_id}/confirm"
            response = requests.patch(url, headers=headers, timeout=10)

            if response.status_code == 204:
                data = response.json()
                order.status = "CONFIRMED"
                order.save()
                return Response(data, status=200)
            return Response({"error": "Failed to confirm order"}, status=response.status_code)
        orders = Order.objects.all()
        orders = OrderSerializer(orders, many=True)
        return Response(orders.data, status=200)


