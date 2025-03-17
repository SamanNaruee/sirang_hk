from django.urls import path
from .views import GetHamrahTokenView, FarmerInfoView, VendorItemsView

urlpatterns = [
    path('get-token/', GetHamrahTokenView.as_view(), name='get-hamrah-token'),
    path('farmer-info/', FarmerInfoView.as_view(), name='farmer-info'),
    path('create-or-update-items/', VendorItemsView.as_view(), name='vendor-items'),
]