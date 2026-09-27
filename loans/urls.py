from django.urls import path
from . import views

urlpatterns = [
    path('', views.loan_list_create, name='loan-list-create'),
    path('<int:pk>/', views.loan_detail, name='loan-detail'),
    path('<int:pk>/approve/', views.loan_approve, name='loan-approve'),
    path('<int:pk>/reject/', views.loan_reject, name='loan-reject'),
]
