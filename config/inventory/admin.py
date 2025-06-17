from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Category)
admin.site.register(Item)
admin.site.register(WareHouseLocation)
admin.site.register(Inventory)
admin.site.register(StockIn)
admin.site.register(StockOut)
admin.site.register(ProfitLossReport)
admin.site.register(Block)
admin.site.register(Customer)
admin.site.register(OrderItem)