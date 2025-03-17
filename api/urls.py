from django.urls import path
from .views import GetHamrahTokenView

urlpatterns = [
    path('get-token/', GetHamrahTokenView.as_view(), name='get-hamrah-token'),
]

