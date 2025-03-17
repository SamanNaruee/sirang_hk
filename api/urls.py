from django.urls import path
from .views import GetHamrahTokenView, FarmerInfoView

urlpatterns = [
    path('get-token/', GetHamrahTokenView.as_view(), name='get-hamrah-token'),
    path('farmer-info/', FarmerInfoView.as_view(), name='farmer-info'),
]