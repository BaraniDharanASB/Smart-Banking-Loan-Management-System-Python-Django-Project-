from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_root, name='dashboard-root'),
]
