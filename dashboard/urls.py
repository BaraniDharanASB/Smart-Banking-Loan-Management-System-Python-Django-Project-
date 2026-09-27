from django.urls import path
from . import views

urlpatterns = [
    path('customer/', views.customer_dashboard, name='customer-dashboard'),
    path('employee/', views.employee_dashboard, name='employee-dashboard'),
    path('admin/', views.admin_dashboard, name='admin-dashboard'),
]
