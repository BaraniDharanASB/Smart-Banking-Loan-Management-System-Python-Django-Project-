from django.urls import path
from . import views

urlpatterns = [
    path('', views.customers_root, name='customers-root'),
]
