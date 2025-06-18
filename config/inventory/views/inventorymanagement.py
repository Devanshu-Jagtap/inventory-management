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
     
class CreateInventoryAPIView(APIView):
    # permission_classes = [IsAuthenticated]

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
    # permission_classes = [IsAuthenticated]

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
    # permission_classes = [IsAuthenticated]
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
    # permission_classes = [IsAuthenticated]
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

        # Get or create customer by phone number, assigning owner
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
            # Generate unique order ID
            order_id = get_random_string(length=8).upper()
            order = Order.objects.create(
                order_id=order_id,
                customer=customer,
                status='confirmed',
                owner=admin_user  # ✅ Set the order owner
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

            return success("Order placed successfully", data={"order_id": order.order_id}, status_code=status.HTTP_201_CREATED)
        
    def get(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return error("Order not found", status_code=status.HTTP_404_NOT_FOUND)

        serializer = OrderDetailSerializer(order)
        return success("Order retrieved successfully", data=serializer.data)


class InventoryTransferAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = StockOutSerializer(data=request.data)
        if not serializer.is_valid():
            return error("Invalid data", serializer.errors)

        inventory_id = serializer.validated_data["inventory_id"]
        quantity = serializer.validated_data["quantity"]
        reason = serializer.validated_data["reason"]

        # Get the inventory record
        try:
            inventory = Inventory.objects.get(id=inventory_id)
        except Inventory.DoesNotExist:
            return error("Inventory not found", status_code=status.HTTP_404_NOT_FOUND)

        # Check stock availability
        if inventory.current_quantity < quantity:
            return error(
                f"Not enough stock. Available: {inventory.current_quantity}"
            )

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

        # return Response({"message": f"{quantity} units removed for reason '{reason}'."}, status=status.HTTP_200_OK)
        return success(f"{quantity} units removed for reason '{reason}'.")


class ItemsInBlockAPIView(APIView):
    # permission_classes = [IsAuthenticated]
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

    # Get all unique items that have inventory entries
    unique_item_ids = Inventory.objects.values_list('item', flat=True).distinct()

    for item_id in unique_item_ids:
        inventories = Inventory.objects.filter(item=item_id)

        # StockIn data for all inventories of this item
        stock_in_data = StockIn.objects.filter(
            inventory__in=inventories,
            created_at__date=today
        ).aggregate(
            total_in=Sum('quantity'),
            total_cost=Sum(F('quantity') * F('cost_price'), output_field=DecimalField())
        )

        # OrderItem data for all inventories of this item
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

        # For reporting, you may want to save one ProfitLossReport per item
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
        ).select_related('inventory__item', 'inventory__block')

        if not reports.exists():
            return Response({"error": "No report found for today"}, status=status.HTTP_404_NOT_FOUND)

        # Prepare file path
        file_name = f"profit_loss_report_{today}.csv"
        report_dir = os.path.join(settings.MEDIA_ROOT, "reports")
        os.makedirs(report_dir, exist_ok=True)
        file_path = os.path.join(report_dir, file_name)

        # Write CSV
        with open(file_path, mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'Inventory ID', 'Item Name', 'Block Name',
                'Total Stock In', 'Total Stock Out',
                'Total Cost', 'Total Revenue', 'Profit', 'Generated On'
            ])
            for report in reports:
                writer.writerow([
                    report.inventory.id,
                    report.inventory.item.name,
                    report.inventory.block.name if report.inventory.block else '',
                    report.total_stock_in,
                    report.total_stock_out,
                    float(report.total_cost),
                    float(report.total_revenue),
                    float(report.profit),
                    report.generated_on.strftime("%Y-%m-%d")
                ])

        # Build and return full URL
        download_url = f"{settings.MEDIA_URL}reports/{file_name}"
        full_url = request.build_absolute_uri(download_url)

        return Response({
            "message": "CSV generated successfully",
            "download_url": full_url
        }, status=status.HTTP_200_OK)

     
class OrderListAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        admin_user = request.user.effective_admin  # Use property, not method
        orders = Order.objects.filter(owner=admin_user).select_related('customer').prefetch_related('items')
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)
    

class CustomerListAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        admin_user = request.user.effective_admin
        customers = Customer.objects.filter(owner=admin_user)
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)
    

class InventorySummaryAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        # Total items = sum of all stock in all blocks (including sold + unsold)
        total_stock_in = (
            Inventory.objects.aggregate(total=Sum('current_quantity'))['total'] or 0
        )

        # Total unsold = current quantity in all blocks
        total_unsold = total_stock_in

        # Total sold from StockOut with reason = 'sale'
        total_sold = (
            StockOut.objects.filter(reason='sale')
            .aggregate(total=Sum('quantity'))['total'] or 0
        )

        # Total damaged from StockOut with reason = 'damage'
        total_damaged = (
            StockOut.objects.filter(reason='damage')
            .aggregate(total=Sum('quantity'))['total'] or 0
        )

        response_data = {
            "total_items": total_unsold + total_sold,  # Total handled
            "total_sold": total_sold,
            "total_unsold": total_unsold,
            "total_damaged": total_damaged
        }

        return Response(response_data, status=status.HTTP_200_OK)
    

class BlockWiseProfitAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user.effective_admin  

        # Step 1: Annotate OrderItems with profit
        order_items = OrderItem.objects.filter(order__owner=user).annotate(
            cost_price=F('item__unit_price'),
            profit=ExpressionWrapper(
                (F('selling_price') - F('item__unit_price')) * F('quantity'),
                output_field=DecimalField()
            )
        )

        # Step 2: Aggregate profits per block
        block_profits = {}
        for item in order_items:
            block = getattr(item.inventory, 'block', None)
            if block:
                block_name = block.name
                block_profits[block_name] = block_profits.get(block_name, Decimal('0')) + item.profit

        total_profit = sum(block_profits.values())
        # Step 3: Format response
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
        start_of_week = today - timedelta(days=today.weekday())  # Monday
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
                .annotate(
                    total=Sum("revenue"),
                    total_quantity=Sum("quantity")
                )
                .order_by("day")
            )

            # Map date → total sales and quantity
            daily_map = {
                sale["day"]: {
                    "amount": float(sale["total"]),
                    "quantity": sale["total_quantity"]
                }
                for sale in sales
            }

            amount_data = []
            quantity_data = []
            total_amount = 0
            total_quantity = 0
            for i in range(7):
                day = start_date + timedelta(days=i)
                day_data = daily_map.get(day, {"amount": 0, "quantity": 0})
                amount_data.append(day_data["amount"])
                quantity_data.append(day_data["quantity"])
                total_amount += day_data["amount"]
                total_quantity += day_data["quantity"]

            return amount_data, quantity_data, total_amount, total_quantity

        # Weekly data
        current_amount, current_qty, current_total, current_total_qty = get_weekly_data(start_of_week)
        prev_amount, prev_qty, prev_total, prev_total_qty = get_weekly_data(start_of_prev_week)

        # Day labels
        categories = list(calendar.day_name)  # Monday → Sunday

        return success("Weekly sales and quantity data fetched successfully", {
            "categories": categories,
            "series": [
                {
                    "name": "Current Week",
                    "data": current_amount,
                    "quantity": current_qty,
                    "total": round(current_total, 2),
                    "total_quantity": current_total_qty
                },
                {
                    "name": "Previous Week",
                    "data": prev_amount,
                    "quantity": prev_qty,
                    "total": round(prev_total, 2),
                    "total_quantity": prev_total_qty
                }
            ]
        })
    

class TopSellingProductsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user.effective_admin

        top_items = (
            OrderItem.objects
            .filter(order__owner=user)
            .values("item__name", "item__sku")
            .annotate(quantity_sold=Sum("quantity"))
            .order_by("-quantity_sold")[:5]
        )

        data = [
            {
                "item_name": item["item__name"],
                "sku": item["item__sku"],
                "quantity_sold": item["quantity_sold"]
            }
            for item in top_items
        ]

        return success("Top selling products fetched successfully", data)