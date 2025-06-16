from django.urls import path
from .views.commanapi import SignupAPIView,LoginAPIView
from .views.employeeapis import EmployeeSignupAPIView,EmployeeListAPIView
from .views.inventorymanagement import InventoryCheckAPIView, StoreItemToInventoryAPIView,ProductWiseQuantityAPIView,TotalAllProductsQuantityAPIView,CreateOrderAPIView,InventoryTransferAPIView
urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('employee-registration/',EmployeeSignupAPIView.as_view(),name='employee-registration'),
    path('employees/', EmployeeListAPIView.as_view(), name='employee-list'),
    path('employees/<int:id>/', EmployeeListAPIView.as_view(), name='employee-detail'),


    #Inventory Management
    path('check-inventory/',InventoryCheckAPIView.as_view()),
    path('add-inventory/',StoreItemToInventoryAPIView.as_view()),
    path('product-wise-total/', ProductWiseQuantityAPIView.as_view(), name='product_wise_total'),
    path('total-quantity/', TotalAllProductsQuantityAPIView.as_view(), name='total_all_products_quantity'),
    path('create-order/',CreateOrderAPIView.as_view(),name="create-order"),
    path('stock-out/', InventoryTransferAPIView.as_view(), name='stock-out'),

    
]
