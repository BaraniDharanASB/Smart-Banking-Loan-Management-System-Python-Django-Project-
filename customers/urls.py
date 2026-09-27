from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.customer_profile, name='customer-profile'),
]
