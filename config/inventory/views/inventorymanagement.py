from django.shortcuts import render
from ..serializers import InventoryStockInSerializer,CustomerSerializer,OrderCreateSerializer,OrderItemInputSerializer,OrderDetailSerializer,StockOutSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..utils import success, error
from ..models import Inventory,Item,Block,StockIn,Customer,Order,OrderItem,StockOut
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum
from django.db import transaction
from django.utils.crypto import get_random_string

class InventoryCheckAPIView(APIView):
    def post(self, request):
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 0))
        
        if not item_id or quantity <= 0:
            return error("Invalid Input", status.HTTP_400_BAD_REQUEST)
        
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return error("Item not found", status.HTTP_404_NOT_FOUND)
        
        suggestions = []
        remaining_quantity = quantity

        blocks = Block.objects.all()

        for block in blocks:
            available_capacity = block.item_capacity - block.used_capacity

            if available_capacity <= 0:
                continue  # Block is full

            if available_capacity >= remaining_quantity:
                suggestions.append({
                    "block_id": block.id,
                    "block_name": block.name,
                    "available_space": available_capacity,
                    "can_store": remaining_quantity
                })
                remaining_quantity = 0
                break
            else:
                suggestions.append({
                    "block_id": block.id,
                    "block_name": block.name,
                    "available_space": available_capacity,
                    "can_store": available_capacity
                })
                remaining_quantity -= available_capacity

        if remaining_quantity > 0:
            return error("Not enough space to store all items", status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "total_required_quantity": quantity,
            "suggestions": suggestions
        }, status=status.HTTP_200_OK)
    

class StoreItemToInventoryAPIView(APIView):
    def post(self, request):
        serializer = InventoryStockInSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        item_id = serializer.validated_data['item_id']
        suggestions = serializer.validated_data['suggestions']

        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            for suggestion in suggestions:
                block_id = suggestion["block_id"]
                quantity_to_store = suggestion["can_store"]

                try:
                    block = Block.objects.get(id=block_id)
                except Block.DoesNotExist:
                    continue  # skip invalid block

                inventory, created = Inventory.objects.get_or_create(
                    item=item,
                    block=block,
                    defaults={"current_quantity": 0}
                )

                inventory.current_quantity += quantity_to_store
                inventory.save()

                block.used_capacity += quantity_to_store
                block.save()

                StockIn.objects.create(
                    inventory=inventory,
                    block=block,
                    quantity=quantity_to_store,
                    cost_price=item.unit_price,
                    added_by=request.user  # must be an authenticated user
                )

        return Response({"message": "Stock successfully added to inventory."}, status=status.HTTP_201_CREATED)


class ProductWiseQuantityAPIView(APIView):
    def get(self, request):
        items = Item.objects.all()
        data = []

        for item in items:
            total_quantity = Inventory.objects.filter(item=item).aggregate(
                total=Sum('current_quantity')
            )['total'] or 0

            data.append({
                "item_id": item.id,
                "item_name": item.name,
                "total_quantity": total_quantity
            })

        return Response(data, status=status.HTTP_200_OK)
    
class TotalAllProductsQuantityAPIView(APIView):
    def get(self, request):
        total_quantity = Inventory.objects.aggregate(
            total=Sum('current_quantity')
        )['total'] or 0

        return Response(
            {"total_all_products_quantity": total_quantity},
            status=status.HTTP_200_OK
        )
    
class CreateOrderAPIView(APIView):
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        customer_data = serializer.validated_data['customer']
        items_data = serializer.validated_data['items']

        # Get or create customer by phone number
        customer, created = Customer.objects.get_or_create(
            customer_phone=customer_data['customer_phone'],
            defaults={
                'customer_name': customer_data['customer_name'],
                'customer_email': customer_data['customer_email'],
                'customer_address': customer_data['customer_address']
            }
        )

        with transaction.atomic():
            # Generate unique order ID (e.g. 8 characters)
            order_id = get_random_string(length=8).upper()
            order = Order.objects.create(
                order_id=order_id,
                customer=customer,
                status='confirmed'
            )

            for item_data in items_data:
                inventory_id = item_data['inventory_id']
                quantity = item_data['quantity']
                selling_price = item_data['selling_price']

                try:
                    inventory = Inventory.objects.select_for_update().get(id=inventory_id)
                except Inventory.DoesNotExist:
                    transaction.set_rollback(True)
                    return Response({"error": f"Inventory ID {inventory_id} not found"}, status=status.HTTP_404_NOT_FOUND)

                if inventory.current_quantity < quantity:
                    transaction.set_rollback(True)
                    return Response({"error": f"Insufficient stock for {inventory.item.name}"}, status=status.HTTP_400_BAD_REQUEST)

                # Reduce stock
                inventory.current_quantity -= quantity
                inventory.save()

                # Create OrderItem
                OrderItem.objects.create(
                    order=order,
                    inventory=inventory,
                    item=inventory.item,
                    quantity=quantity,
                    selling_price=selling_price
                )

                # Create StockOut
                StockOut.objects.create(
                    inventory=inventory,
                    quantity=quantity,
                    reason='sale',
                    removed_by=request.user if request.user.is_authenticated else None
                )

            return Response({"message": "Order placed successfully", "order_id": order.order_id}, status=status.HTTP_201_CREATED)
        

    def get(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderDetailSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InventoryTransferAPIView(APIView):
    def post(self, request):
        serializer = StockOutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        inventory_id = serializer.validated_data["inventory_id"]
        quantity = serializer.validated_data["quantity"]
        reason = serializer.validated_data["reason"]

        # Get the inventory record
        try:
            inventory = Inventory.objects.get(id=inventory_id)
        except Inventory.DoesNotExist:
            return Response({"error": "Inventory not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check stock availability
        if inventory.current_quantity < quantity:
            return Response({
                "error": f"Not enough stock. Available: {inventory.current_quantity}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Deduct quantity
        inventory.current_quantity -= quantity
        inventory.save()

        # Record the stock out
        StockOut.objects.create(
            inventory=inventory,
            quantity=quantity,
            reason=reason,
            date=timezone.now(),
            removed_by=request.user
        )

        return Response({"message": f"{quantity} units removed for reason '{reason}'."}, status=status.HTTP_200_OK)
