# users/serializers.py
from rest_framework import serializers
from .models import CustomUser,Order,OrderItem,Customer

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
    suggestions = InventoryStockInSuggestionSerializer(many=True)



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