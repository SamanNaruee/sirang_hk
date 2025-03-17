from django.urls import path
from .views import GetHamrahTokenView, FarmerUserInfoView, VendorItemsView, OrderCreateView, ProductsView ,OrderStatusView\
, OrderConfirmView

urlpatterns = [
    path('get-token/', GetHamrahTokenView.as_view(), name='get-hamrah-token'),
    path('farmer-info/', FarmerUserInfoView.as_view(), name='farmer-info'),
    path('create-or-update-items/', VendorItemsView.as_view(), name='vendor-items'),
    path('create-order/', OrderCreateView.as_view(), name='create-order'),
    path('order-status/', OrderStatusView.as_view(), name='all-orders-status'),
    path('order-status/<uuid:order_id>/', OrderStatusView.as_view(), name='order-status-detail'),
    path('order-confirm/', OrderConfirmView.as_view(), name='orders-for-confirm'),
    path('order-confirm/<uuid:order_id>/', OrderConfirmView.as_view(), name='order-confirm-detail'),
    

    # Products
    path('products/', ProductsView.as_view(), name='products'),
    path('products/<uuid:product_id>/', ProductsView.as_view(), name='product-detail'), 
]