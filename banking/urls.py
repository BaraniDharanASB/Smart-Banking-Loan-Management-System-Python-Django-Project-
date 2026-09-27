from django.urls import path
from . import views

urlpatterns = [
    path('', views.banking_root, name='banking-root'),
]
