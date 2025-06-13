from django.urls import path
from .views import SignupAPIView,LoginAPIView,EmployeeSignupAPIView,EmployeeListAPIView

urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('employee-registration/',EmployeeSignupAPIView.as_view(),name='employee-registration'),
    path('employees/', EmployeeListAPIView.as_view(), name='employee-list'),
    path('employees/<int:id>/', EmployeeListAPIView.as_view(), name='employee-detail'),
    
]
