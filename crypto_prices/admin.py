from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from .models import CryptoPrice, Purchase
import requests

class CryptoPriceAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'price']
    list_filter = ['symbol']
    search_fields = ['symbol']

    def get_binance_data(self):
        url = 'https://api.binance.com/api/v3/ticker/price'
        response = requests.get(url)
        data = response.json()
        return data

    def save_model(self, request, obj, form, change):
        if not change:
            binance_data = self.get_binance_data()
            symbol = form.cleaned_data['symbol']
            for item in binance_data:
                if item['symbol'] == symbol:
                    obj.price = item['price']
                    break
        obj.save()

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('buy_max/<int:purchase_id>/', self.buy_max_view, name='buy_max'),
        ]
        return custom_urls + urls

    def buy_max_view(self, request, purchase_id):
        purchase = Purchase.objects.get(pk=purchase_id)
        crypto = purchase.crypto
        user_balance = 1000  # Set the user's balance here (in this example, it's 1000 USD)
        max_quantity = user_balance / crypto.price

        # Update the quantity to the max value
        purchase.quantity = max_quantity
        purchase.save()

        # Redirect back to the Purchase change page
        return redirect('admin:appname_purchase_change', purchase_id)

class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'crypto', 'quantity', 'timestamp', 'max_quantity']
    list_filter = ['user', 'crypto']
    search_fields = ['user__username', 'crypto__symbol']
    readonly_fields = ['max_quantity']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['quantity'].required = False
        return form

    def max_quantity(self, obj=None):
        if obj and obj.crypto and obj.crypto.price:
            user_balance = 100  # Max amount in USD that the user can spend (100 USD in this example)
            max_quantity = user_balance / obj.crypto.price
            return max_quantity
        return None

    def save_model(self, request, obj, form, change):
        if obj.quantity and obj.crypto and obj.crypto.price:
            user_balance = 100  # Max amount in USD that the user can spend (100 USD in this example)
            max_quantity = user_balance / obj.crypto.price
            obj.quantity = min(obj.quantity, max_quantity)
        super().save_model(request, obj, form, change)

    max_quantity.short_description = 'Max'
    max_quantity.admin_order_field = 'crypto__price'

    def buy_max_action(self, request, queryset):
        for purchase in queryset:
            purchase.quantity = self.max_quantity(purchase)
            purchase.save()

    buy_max_action.short_description = 'Buy Max'

    actions = [buy_max_action]

admin.site.register(CryptoPrice, CryptoPriceAdmin)
admin.site.register(Purchase, PurchaseAdmin)