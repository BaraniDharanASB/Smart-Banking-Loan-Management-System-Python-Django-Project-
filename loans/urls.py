from django.urls import path
from . import views

urlpatterns = [
    path('', views.loans_root, name='loans-root'),
]
