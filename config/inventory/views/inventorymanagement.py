from django.shortcuts import render
from ..serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..utils import success, error
from ..models import *
from rest_framework.response import Response
from django.utils import timezone
from django.utils.timezone import now, timedelta
from django.db.models.functions import TruncDate
from django.db.models import F, Sum, DecimalField, ExpressionWrapper
from django.db import transaction
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
import csv
import os
from django.utils.timezone import now
from django.conf import settings
from decimal import Decimal
from django.db.models import Sum, F, DecimalField
import calendar

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
    
    
class CreateInventoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = InventoryStockInSerializer(data=request.data)
        if not serializer.is_valid():
            return error("Invalid input", serializer.errors)

        item_id = serializer.validated_data['item_id']
        block_id = serializer.validated_data['block_id']
        quantity = serializer.validated_data['quantity']

        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return error("Item not found", status.HTTP_404_NOT_FOUND)

        try:
            block = Block.objects.get(id=block_id)
        except Block.DoesNotExist:
            return error("Block not found", status.HTTP_404_NOT_FOUND)

        if Inventory.objects.filter(item=item, block=block).exists():
            return error("Inventory for this item and block already exists")

        if block.available_capacity() < quantity:
            return error("Not enough block capacity")

        user = CustomUser.objects.get(id=2)  # request.user if using auth

        with transaction.atomic():
            inventory = Inventory.objects.create(
                item=item,
                block=block,
                current_quantity=quantity
            )
            block.used_capacity += quantity
            block.save()

            StockIn.objects.create(
                inventory=inventory,
                quantity=quantity,
                cost_price=item.unit_price,
                added_by=user
            )

        return success("Inventory created successfully", status.HTTP_201_CREATED)


class UpdateInventoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = InventoryStockInSerializer(data=request.data)
        if not serializer.is_valid():
            return error("Invalid input", serializer.errors)

        item_id = serializer.validated_data['item_id']
        block_id = serializer.validated_data['block_id']
        quantity = serializer.validated_data['quantity']

        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return error("Item not found", status.HTTP_404_NOT_FOUND)

        try:
            block = Block.objects.get(id=block_id)
        except Block.DoesNotExist:
            return error("Block not found", status.HTTP_404_NOT_FOUND)

        try:
            inventory = Inventory.objects.get(item=item, block=block)
        except Inventory.DoesNotExist:
            return error("Inventory does not exist, please create it first", status.HTTP_404_NOT_FOUND)

        if block.available_capacity() < quantity:
            return error("Not enough available capacity in block")

        user = CustomUser.objects.get(id=2)  # request.user

        with transaction.atomic():
            inventory.current_quantity += quantity
            inventory.save()

            block.used_capacity += quantity
            block.save()

            StockIn.objects.create(
                inventory=inventory,
                quantity=quantity,
                cost_price=item.unit_price,
                added_by=user
            )

        return success("Inventory quantity updated successfully", status.HTTP_200_OK)


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

        return success("Product-wise quantity retrieved successfully", data=data)
    
class TotalAllProductsQuantityAPIView(APIView):
    def get(self, request):
        total_quantity = Inventory.objects.aggregate(
            total=Sum('current_quantity')
        )['total'] or 0

        return success(
            "Total quantity of all products retrieved successfully",
            data={"total_all_products_quantity": total_quantity}
        )



class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error("Invalid order data", serializer.errors)

        customer_data = serializer.validated_data['customer']
        items_data = serializer.validated_data['items']

        admin_user = request.user.effective_admin  

        
        customer, created = Customer.objects.get_or_create(
            customer_phone=customer_data['customer_phone'],
            owner=admin_user,
            defaults={
                'customer_name': customer_data['customer_name'],
                'customer_email': customer_data['customer_email'],
                'customer_address': customer_data['customer_address']
            }
        )

        with transaction.atomic():
            
            order_id = get_random_string(length=8).upper()
            order = Order.objects.create(
                order_id=order_id,
                customer=customer,
                status='confirmed',
                owner=admin_user  
            )

            for item_data in items_data:
                inventory_id = item_data['inventory_id']
                quantity = item_data['quantity']
                selling_price = item_data['selling_price']

                try:
                    inventory = Inventory.objects.select_for_update().get(id=inventory_id)
                except Inventory.DoesNotExist:
                    transaction.set_rollback(True)
                    return error(f"Inventory ID {inventory_id} not found", status_code=status.HTTP_404_NOT_FOUND)

                if inventory.current_quantity < quantity:
                    transaction.set_rollback(True)
                    return error(f"Insufficient stock for {inventory.item.name}")

                
                inventory.current_quantity -= quantity
                inventory.save()

               
                OrderItem.objects.create(
                    order=order,
                    inventory=inventory,
                    item=inventory.item,
                    quantity=quantity,
                    selling_price=selling_price
                )

                
                StockOut.objects.create(
                    inventory=inventory,
                    quantity=quantity,
                    reason='sale',
                    removed_by=request.user if request.user.is_authenticated else None
                )

            return success("Order placed successfully", data={"order_id": order.order_id}, status_code=status.HTTP_201_CREATED)
        
    def get(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return error("Order not found", status_code=status.HTTP_404_NOT_FOUND)

        serializer = OrderDetailSerializer(order)
        return success("Order retrieved successfully", data=serializer.data)


class InventoryTransferAPIView(APIView):
    def post(self, request):
        serializer = StockOutSerializer(data=request.data)
        if not serializer.is_valid():
            return error("Invalid data", serializer.errors)

        inventory_id = serializer.validated_data["inventory_id"]
        quantity = serializer.validated_data["quantity"]
        reason = serializer.validated_data["reason"]

       
        try:
            inventory = Inventory.objects.get(id=inventory_id)
        except Inventory.DoesNotExist:
            return error("Inventory not found", status_code=status.HTTP_404_NOT_FOUND)

        
        if inventory.current_quantity < quantity:
            return error(
                f"Not enough stock. Available: {inventory.current_quantity}"
            )

        inventory.current_quantity -= quantity
        inventory.save()

      
        StockOut.objects.create(
            inventory=inventory,
            quantity=quantity,
            reason=reason,
            date=timezone.now(),
            removed_by=request.user
        )

        
        return success(f"{quantity} units removed for reason '{reason}'.")


class ItemsInBlockAPIView(APIView):
    def get(self, request, block_id):
        block = get_object_or_404(Block, id=block_id)
        inventory_items = Inventory.objects.filter(block=block).select_related('item')
        block_available=int(block.item_capacity)-int(block.used_capacity)
        serializer = BlockInventoryItemSerializer(inventory_items, many=True)
        return Response({
            "block_id": block.id,
            "block_name": block.name,
            "block_capacity":block.item_capacity,
            "block_used_capacity":block.used_capacity,
            "block_available_capacity":block_available,
            "items": serializer.data
        }, status=status.HTTP_200_OK)



def generate_daily_profit_loss_report():
    today = timezone.now().date()

    unique_item_ids = Inventory.objects.values_list('item', flat=True).distinct()

    for item_id in unique_item_ids:
        inventories = Inventory.objects.filter(item=item_id)

        
        stock_in_data = StockIn.objects.filter(
            inventory__in=inventories,
            created_at__date=today
        ).aggregate(
            total_in=Sum('quantity'),
            total_cost=Sum(F('quantity') * F('cost_price'), output_field=DecimalField())
        )

        order_items_data = OrderItem.objects.filter(
            inventory__in=inventories,
            date__date=today
        ).aggregate(
            total_out=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('selling_price'), output_field=DecimalField())
        )

        total_stock_in = stock_in_data['total_in'] or 0
        total_stock_out = order_items_data['total_out'] or 0
        total_cost = stock_in_data['total_cost'] or 0
        total_revenue = order_items_data['total_revenue'] or 0
        profit = total_revenue - total_cost

        
        ProfitLossReport.objects.update_or_create(
            item_id=item_id,
            generated_on=today,
            defaults={
                'total_stock_in': total_stock_in,
                'total_stock_out': total_stock_out,
                'total_cost': total_cost,
                'total_revenue': total_revenue,
                'profit': profit
            }
        )

    return f"Profit & Loss reports generated for {len(unique_item_ids)} items."




class ExportTodayProfitLossCSVAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()

        reports = ProfitLossReport.objects.filter(
            generated_on__date=today
        ).select_related('item')

        if not reports.exists():
            return Response(
                {"error": "No report found for today"},
                status=status.HTTP_404_NOT_FOUND
            )

        file_name = f"profit_loss_report_{today}.csv"
        report_dir = os.path.join(settings.MEDIA_ROOT, "reports")
        os.makedirs(report_dir, exist_ok=True)
        file_path = os.path.join(report_dir, file_name)

        with open(file_path, mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'Item Name',
                'Total Stock In', 'Total Stock Out',
                'Total Cost', 'Total Revenue', 'Profit', 'Generated On'
            ])
            for report in reports:
                writer.writerow([
                    report.item.name,
                    report.total_stock_in,
                    report.total_stock_out,
                    float(report.total_cost),
                    float(report.total_revenue),
                    float(report.profit),
                    report.generated_on.strftime("%Y-%m-%d")
                ])

        download_url = f"{settings.MEDIA_URL}reports/{file_name}"
        full_url = request.build_absolute_uri(download_url)

        return Response({
            "message": "CSV generated successfully",
            "download_url": full_url
        }, status=status.HTTP_200_OK)


class OrderListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        admin_user = request.user.effective_admin  
        orders = Order.objects.filter(owner=admin_user).select_related('customer').prefetch_related('items')
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)
    

class CustomerListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        admin_user = request.user.effective_admin
        customers = Customer.objects.filter(owner=admin_user)
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)
    

class InventorySummaryAPIView(APIView):
    def get(self, request):
        
        total_stock_in = (
            Inventory.objects.aggregate(total=Sum('current_quantity'))['total'] or 0
        )

        
        total_unsold = total_stock_in

        
        total_sold = (
            StockOut.objects.filter(reason='sale')
            .aggregate(total=Sum('quantity'))['total'] or 0
        )

       
        total_damaged = (
            StockOut.objects.filter(reason='damage')
            .aggregate(total=Sum('quantity'))['total'] or 0
        )

        response_data = {
            "total_items": total_unsold + total_sold, 
            "total_sold": total_sold,
            "total_unsold": total_unsold,
            "total_damaged": total_damaged
        }

        return Response(response_data, status=status.HTTP_200_OK)
    

class BlockWiseProfitAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user.effective_admin  
        order_items = OrderItem.objects.filter(order__owner=user).annotate(
            cost_price=F('item__unit_price'),
            profit=ExpressionWrapper(
                (F('selling_price') - F('item__unit_price')) * F('quantity'),
                output_field=DecimalField()
            )
        )

        

        block_profits = {}
        for item in order_items:
            block = getattr(item.inventory, 'block', None)
            if block:
                block_name = block.name
                block_profits[block_name] = block_profits.get(block_name, Decimal('0')) + item.profit

        total_profit = sum(block_profits.values())
        print(total_profit)
        print(block_profits)
       
        data = []
        for block_name, profit in block_profits.items():
            percent = (profit / total_profit * 100) if total_profit > 0 else 0
            data.append({
                "block": block_name,
                "profit": round(profit, 2),
                "percent": round(percent, 2)
            })

        return success("Block-wise profit percentage fetched successfully", {
            "total_profit": round(total_profit, 2),
            "block_wise_data": data
        })
    

class WeeklySalesChartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user.effective_admin
        today = now().date()
        start_of_week = today - timedelta(days=today.weekday())  
        start_of_prev_week = start_of_week - timedelta(days=7)

        def get_weekly_data(start_date):
            end_date = start_date + timedelta(days=6)
            sales = (
                OrderItem.objects.filter(order__owner=user, date__date__range=(start_date, end_date))
                .annotate(
                    revenue=ExpressionWrapper(
                        F("selling_price") * F("quantity"), output_field=DecimalField()
                    )
                )
                .annotate(day=TruncDate("date"))
                .values("day")
                .annotate(total=Sum("revenue"))
                .order_by("day")
            )

            daily_map = {sale["day"]: float(sale["total"]) for sale in sales}

            data = []
            total = 0
            for i in range(7):
                day = start_date + timedelta(days=i)
                amount = daily_map.get(day, 0)
                data.append(amount)
                total += amount
            return data, total

        
        current_week_data, current_week_total = get_weekly_data(start_of_week)
        prev_week_data, prev_week_total = get_weekly_data(start_of_prev_week)

     
        categories = list(calendar.day_name)  
        return success("Weekly sales fetched successfully", {
            "categories": categories,
            "series": [
                {
                    "name": "Current Week",
                    "data": current_week_data,
                    "total": round(current_week_total, 2)
                },
                {
                    "name": "Previous Week",
                    "data": prev_week_data,
                    "total": round(prev_week_total, 2)
                }
            ]
        })