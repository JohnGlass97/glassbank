from django.contrib import admin

# Register your models here.
from .models import Account, ConversionRate, ShopItem, Transaction, MoneyRequest
admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(MoneyRequest)
admin.site.register(ShopItem)
admin.site.register(ConversionRate)
