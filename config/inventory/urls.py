from django.urls import path
from .views.commanapi import SignupAPIView,LoginAPIView,EmployeeSignupAPIView,EmployeeListAPIView
from django.urls import path
from .views.adminapi import *


urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('employee-registration/',EmployeeSignupAPIView.as_view(),name='employee-registration'),
    path('employees/', EmployeeListAPIView.as_view(), name='employee-list'),
    path('employees/<int:id>/', EmployeeListAPIView.as_view(), name='employee-detail'),
    path('categories/listview/', CategoryListAPIView.as_view(), name='category-list'),
    path('categories/create/', CategoryCreateAPIView.as_view(), name='category-create'),
    path('categories/update/<int:pk>/', CategoryUpdateAPIView.as_view(), name='category-update'),
    path('categories/delete/<int:pk>/', CategoryDeleteAPIView.as_view(), name='category-delete'),
    path('items/listview/', ItemListAPIView.as_view(), name='item-list'),
    path('items/create/', ItemCreateAPIView.as_view(), name='item-create'),
    path('items/update/<int:pk>/', ItemUpdateAPIView.as_view(), name='item-update'),
    path('items/delete/<int:pk>/', ItemDeleteAPIView.as_view(), name='item-delete'),
    path('items/detail/<int:pk>/', ItemDetailAPIView.as_view(), name='item-detail'),
    path('employee/listview/', EmployeeListAPIView.as_view(), name='user-list'),
    path('employee/create/', EmployeeCreateAPIView.as_view(), name='user-create'),
    path('employee/update/<int:pk>/', EmployeeUpdateAPIView.as_view(), name='user-update'),
    path('employee/delete/<int:pk>/', EmployeeDeleteAPIView.as_view(), name='user-delete'),
    path('employee/detail/<int:pk>/', EmployeeDetailAPIView.as_view(), name='user-detail'),
    path('warehouses/listview/', WareHouseLocationListAPIView.as_view(), name='warehouse-list'),
    path('warehouses/create/', WareHouseLocationCreateAPIView.as_view(), name='warehouse-create'),
    path('warehouses/<int:pk>/', WareHouseLocationRetrieveAPIView.as_view(), name='warehouse-retrieve'),
    path('warehouses/update/<int:pk>/', WareHouseLocationUpdateAPIView.as_view(), name='warehouse-update'),
    path('warehouses/delete/<int:pk>/', WareHouseLocationDeleteAPIView.as_view(), name='warehouse-delete'),
    path('blocks/create/', BlockCreateView.as_view()),
    path('blocks/listview/', BlockListView.as_view()),
    path('blocks/update/<int:pk>/', BlockUpdateView.as_view()),
    path('blocks/delete/<int:pk>/', BlockDeleteView.as_view()),

]
    
    


