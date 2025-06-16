from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from .basecontent import BaseContent
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('user_type', CustomUser.UserType.ADMIN)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)  # Required for Django admin access
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    class UserType(models.TextChoices):
        ADMIN = "admin", "Admin"
        EMPLOYEE = "employee", "Employee"

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    number = models.CharField(max_length=15, blank=True, null=True)

    user_type = models.CharField(max_length=10, choices=UserType.choices, default=UserType.EMPLOYEE)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Needed for Django admin
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email



#Master

class Category(BaseContent):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Item(BaseContent):
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # description = models.TextField(blank=True, null=True) 
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.sku})"

class WareHouseLocation(BaseContent):
    name = models.CharField(max_length=255,null=True,blank=True)
    address = models.TextField(blank=True, null=True)
    block_capacity = models.PositiveIntegerField(help_text="Total capacity of the warehouse (in units)",default=0)
    used_capacity = models.PositiveIntegerField(default=0)

    manager = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    def available_capacity(self):
        return self.block_capacity - self.used_capacity

    def __str__(self):
        return f"{self.name}"
    

class Block(BaseContent):
    warehouse = models.ForeignKey(WareHouseLocation, on_delete=models.CASCADE,blank=True,null=True)
    name = models.CharField(max_length=100)
    item_capacity = models.PositiveIntegerField(help_text="Capacity of this block")
    used_capacity = models.PositiveIntegerField(default=0)

    def available_capacity(self):
        return self.item_capacity - self.used_capacity

    def __str__(self):
        return f"{self.name} in {self.warehouse.name}"

class Inventory(BaseContent):
    item = models.ForeignKey(Item, on_delete=models.CASCADE,blank=True,null=True)
    block = models.ForeignKey(Block, on_delete=models.CASCADE,blank=True,null=True)
    current_quantity = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.item.name} @ {self.block.name}"
    
class StockIn(BaseContent):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE,blank=True,null=True)
    quantity = models.PositiveIntegerField()
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"In: {self.quantity} of {self.inventory.item.name}"

class StockOut(BaseContent):
    REASON_CHOICES = [
        ('sale', 'Sale'),
        ('transfer', 'Transfer'),
        ('damage', 'Damage'),
    ]

    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE,blank=True,null=True)
    quantity = models.PositiveIntegerField()
    reason = models.CharField(max_length=10, choices=REASON_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    removed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Out: {self.quantity} of {self.inventory.item.name} ({self.reason})"


class ProfitLossReport(BaseContent):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE,blank=True,null=True)
    location = models.ForeignKey(WareHouseLocation, on_delete=models.CASCADE,blank=True,null=True)

    total_stock_in = models.PositiveIntegerField(default=0)
    total_stock_out = models.PositiveIntegerField(default=0)

    total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    profit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    generated_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('inventory', 'location', 'generated_on')
        verbose_name = "Profit & Loss Report"
        verbose_name_plural = "Profit & Loss Reports"

    def __str__(self):
        return f"{self.inventory.item.name} @ ({self.generated_on.date()}"

class Customer(BaseContent):
    customer_name = models.CharField(max_length=225)
    customer_phone = models.CharField(max_length=15)
    customer_email = models.EmailField(unique=True)
    customer_address = models.TextField()

    def __str__(self):
        return f"customer {self.customer_name}"
class Order(BaseContent):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('cancelled', 'Cancelled'),
    ]

    order_id = models.CharField(max_length=10, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=15, choices=ORDER_STATUS, default='pending')
    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.customer.customer_name}"

class OrderItem(BaseContent):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    inventory = models.ForeignKey(Inventory, on_delete=models.SET_NULL, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE,blank=True,null=True)
    quantity = models.PositiveIntegerField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)  # price at time of order
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.quantity} x {self.inventory.item.name} in {self.order.order_id}"
    

