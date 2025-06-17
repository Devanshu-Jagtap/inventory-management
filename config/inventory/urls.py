from django.urls import path
from .views.commanapi import SignupAPIView,LoginAPIView
from .views.employeeapis import EmployeeSignupAPIView,EmployeeListAPIView
from .views.inventorymanagement import *
from .views.commanapi import *
from django.urls import path
from .views.adminapi import *


urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('employee-registration/',EmployeeSignupAPIView.as_view(),name='employee-registration'),
    path('employees/', EmployeeListAPIView.as_view(), name='employee-list'),
    path('employees/<int:id>/', EmployeeListAPIView.as_view(), name='employee-detail'),
    path('export-profit-loss-today/', ExportTodayProfitLossCSVAPIView.as_view()),
    path('item-wise-profit/', OverallItemWiseProfitAPIView.as_view()),
    path('category-wise-profit/', CategoryWiseProfitAPIView.as_view()),

    #Inventory Management
    path('check-inventory/',InventoryCheckAPIView.as_view()),
    path('add-inventory/',StoreItemToInventoryAPIView.as_view()),
    path('product-wise-total/', ProductWiseQuantityAPIView.as_view(), name='product_wise_total'),
    path('total-quantity/', TotalAllProductsQuantityAPIView.as_view(), name='total_all_products_quantity'),
    path('create-order/',CreateOrderAPIView.as_view(),name="create-order"),
    path('stock-out/', InventoryTransferAPIView.as_view(), name='stock-out'),
    path('block-items/<int:block_id>/', ItemsInBlockAPIView.as_view(), name='block-items'),
    path('inventory-management/add-inventory/',StoreItemToInventoryAPIView.as_view()),
    path('categories/listview/', CategoryListAPIView.as_view(), name='category-list'),
    path('categories/create/', CategoryCreateAPIView.as_view(), name='category-create'),
    path('categories/update/<int:pk>/', CategoryUpdateAPIView.as_view(), name='category-update'),
    path('categories/delete/<int:pk>/', CategoryDeleteAPIView.as_view(), name='category-delete'),
    path('items/listview/', ItemListAPIView.as_view(), name='item-list'),
    path('items/create/', ItemCreateAPIView.as_view(), name='item-create'),
    path('items/update/<int:pk>/', ItemUpdateAPIView.as_view(), name='item-update'),
    path('items/delete/<int:pk>/', ItemDeleteAPIView.as_view(), name='item-delete'),
    path('inventory-management/check-inventory/',InventoryCheckAPIView.as_view()),
    path('inventory-management/add-inventory/',StoreItemToInventoryAPIView.as_view()),
    path('inventory-management/product-wise-total/', ProductWiseQuantityAPIView.as_view(), name='product_wise_total'),
    path('inventory-management/total-quantity/', TotalAllProductsQuantityAPIView.as_view(), name='total_all_products_quantity'),
    path('inventory-management/create-order/',CreateOrderAPIView.as_view(),name="create-order"),
    path('inventory-management/stock-out/', InventoryTransferAPIView.as_view(), name='stock-out'),

    
    path('categories/listview/', CategoryAPIView.as_view(), name='category-list'),
    path('categories/create/', CategoryAPIView.as_view(), name='category-create'),
    path('categories/update/<int:pk>/', CategoryAPIView.as_view(), name='category-update'),
    path('categories/delete/<int:pk>/', CategoryAPIView.as_view(), name='category-delete'),
    # path('items/listview/', ItemListAPIView.as_view(), name='item-list'),
    path('items/listview/', ItemAPIView.as_view(), name='item-create'),
    path('items/create/', ItemAPIView.as_view(), name='item-create'),
    path('items/update/<int:pk>/', ItemAPIView.as_view(), name='item-update'),
    path('items/delete/<int:pk>/', ItemAPIView.as_view(), name='item-delete'),
    path('items/detail/<int:pk>/', ItemDetailAPIView.as_view(), name='item-detail'),
    path('employee/listview/', EmployeeListAPIView.as_view(), name='user-list'),
    path('employee/create/', EmployeeCreateAPIView.as_view(), name='user-create'),
    path('employee/update/<int:pk>/', EmployeeUpdateAPIView.as_view(), name='user-update'),
    path('employee/delete/<int:pk>/', EmployeeDeleteAPIView.as_view(), name='user-delete'),
    path('employee/detail/<int:pk>/', EmployeeDetailAPIView.as_view(), name='user-detail'),
    path('warehouses/listview/', WareHouseLocationAPIView.as_view(), name='warehouse-list'),
    path('warehouses/create/', WareHouseLocationAPIView.as_view(), name='warehouse-create'),
    path('warehouses/<int:pk>/', WareHouseLocationAPIView.as_view(), name='warehouse-retrieve'),
    path('warehouses/update/<int:pk>/', WareHouseLocationAPIView.as_view(), name='warehouse-update'),
    path('warehouses/delete/<int:pk>/', WareHouseLocationAPIView.as_view(), name='warehouse-delete'),
    path('blocks/create/', BlockAPIView.as_view()),
    path('blocks/listview/', BlockAPIView.as_view()),
    path('blocks/update/<int:pk>/', BlockAPIView.as_view()),
    path('blocks/delete/<int:pk>/', BlockAPIView.as_view()),

]
    
    


