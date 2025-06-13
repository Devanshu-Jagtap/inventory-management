
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from basecontent import BaseContent
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
    description = models.TextField(blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.sku})"

class Country(BaseContent):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=5)

    def __str__(self):
        return self.name


class State(BaseContent):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    code = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.name} ({self.country.name})"


class City(BaseContent):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    code = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.name} ({self.state.name})"

class WareHouseLocation(BaseContent):
    address = models.TextField()
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    manager = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.address} - {self.city.name}"
    
class Inventory(BaseContent):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    location = models.ForeignKey(WareHouseLocation, on_delete=models.CASCADE)
    current_quantity = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.item.name} @ {self.location.city.name}"
    
class StockIn(BaseContent):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
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

    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=10, choices=REASON_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    removed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Out: {self.quantity} of {self.inventory.item.name} ({self.reason})"


class ProfitLossReport(BaseContent):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    location = models.ForeignKey(WareHouseLocation, on_delete=models.CASCADE)

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
        return f"{self.inventory.item.name} @ {self.location.city.name} ({self.generated_on.date()}"
