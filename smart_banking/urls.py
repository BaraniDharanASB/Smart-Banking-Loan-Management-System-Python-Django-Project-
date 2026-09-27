from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/customers/', include('customers.urls')),
    path('api/banking/', include('banking.urls')),
    path('api/loans/', include('loans.urls')),
    path('api/dashboard/', include('dashboard.urls')),
]
