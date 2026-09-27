from django.urls import path
from . import views

urlpatterns = [
    path('accounts/', views.account_list_create, name='account-list-create'),
    path('accounts/<int:pk>/', views.account_detail, name='account-detail'),
]
