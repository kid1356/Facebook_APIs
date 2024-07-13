from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import *

# router = DefaultRouter()
# router.register(r'register/', RegisterView, basename='register')


urlpatterns = [
    path('register/', RegisterView.as_view(), name = 'register'),
    path('login/', LoginView.as_view(), name = 'login'),
    path('change-password/', ChangePasswordView.as_view(), name = 'change-password'),
    path('update/<int:id>/', UpdateUserInfoView.as_view(), name = 'update-info'),
    path('forget-password-email/', ForgetPasswordEmailView.as_view(), name = 'send-email'),
    path('forget-password/', ForgetPasswordView.as_view(), name = 'forget-password-recovery'),
    path('activate-user/<int:id>/', ActiveUserView.as_view(), name = 'active-user'),
    path('deactivate-user/<int:id>/', DeActiveUserView.as_view(), name = 'de-active-user'),
    
    
]