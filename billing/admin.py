from django.contrib import admin
from .models import Transaction

from django.contrib import admin
from .models import Transaction, Item

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_fruit_name', 'weight', 'get_price_per_kg', 'total_price', 'timestamp')

    def get_fruit_name(self, obj): 
        return obj.item.name
    get_fruit_name.short_description = 'Fruit Name'

    def get_price_per_kg(self, obj):
        return obj.item.price_per_kg
    get_price_per_kg.short_description = 'Price per Kg'


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_per_kg', 'available')
