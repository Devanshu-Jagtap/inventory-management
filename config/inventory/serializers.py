# users/serializers.py
from rest_framework import serializers
from .models import *

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)


    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'password', 'number', 'user_type']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email', 'user_type'] 


class InventoryStockInSuggestionSerializer(serializers.Serializer):
    block_id = serializers.IntegerField()
    can_store = serializers.IntegerField(min_value=1)


class InventoryStockInSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    block_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

class CustomerSerializer(serializers.Serializer):
    customer_name = serializers.CharField(max_length=225)
    customer_phone = serializers.CharField(max_length=15)
    customer_email = serializers.EmailField()
    customer_address = serializers.CharField()

class OrderItemInputSerializer(serializers.Serializer):
    inventory_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    selling_price = serializers.DecimalField(max_digits=10, decimal_places=2)

class OrderCreateSerializer(serializers.Serializer):
    customer = CustomerSerializer()
    items = OrderItemInputSerializer(many=True)



class CustomerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_name', 'customer_phone', 'customer_email', 'customer_address']

class OrderItemDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name')

    class Meta:
        model = OrderItem
        fields = ['item_name', 'quantity', 'selling_price']

class OrderDetailSerializer(serializers.ModelSerializer):
    customer = CustomerDetailSerializer()
    items = OrderItemDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['order_id', 'status', 'ordered_at', 'customer', 'items']


class StockOutSerializer(serializers.Serializer):
    inventory_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    reason = serializers.ChoiceField(choices=["transfer", "damage"])
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'
        read_only_fields = ['owner']



class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # don't return password

    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email', 'user_type', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)  # hashes the password
        user.save()
        return user



class WareHouseLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WareHouseLocation
        fields = '__all__'


class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = '__all__'


class BlockInventoryItemSerializer(serializers.ModelSerializer):
    item_id = serializers.IntegerField(source='item.id')
    item_name = serializers.CharField(source='item.name')
    item_sku = serializers.CharField(source='item.sku')
    category = serializers.CharField(source='item.category.name')
    unit_price = serializers.DecimalField(source='item.unit_price', max_digits=10, decimal_places=2)
    current_quantity = serializers.IntegerField()

    class Meta:
        model = Inventory
        fields = ['item_id',
            'item_name',
            'item_sku',
            'category',
            'unit_price',
            'current_quantity']



class InventoryStockInSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    block_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'item', 'quantity', 'selling_price', 'date']

class OrderListSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'order_id', 'customer', 'status', 'ordered_at', 'items']