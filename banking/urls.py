from django.urls import path
from . import views

urlpatterns = [
    path('accounts/', views.account_list_create, name='account-list-create'),
    path('accounts/<int:pk>/', views.account_detail, name='account-detail'),
    path('deposit/', views.deposit_view, name='deposit'),
    path('withdraw/', views.withdraw_view, name='withdraw'),
    path('transfer/', views.transfer_view, name='transfer'),
    path('transactions/', views.transaction_list, name='transaction-list'),
]
