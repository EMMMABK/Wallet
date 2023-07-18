# admin.py
from django import forms
from django.contrib import admin
from .models import CryptoPrice, Purchase
import requests
from django.urls import path

class PurchaseForm(forms.ModelForm):
    dollar_amount = forms.DecimalField(label='Quantity ($)', decimal_places=2, required=False)

    class Meta:
        model = Purchase
        fields = ['user', 'crypto', 'dollar_amount']

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
            symbol = form.cleaned_data['crypto']  # 'symbol' was incorrect, it should be 'crypto'
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
    list_display = ['user', 'crypto', 'quantity_in_dollars', 'timestamp', 'max_quantity']
    list_filter = ['user', 'crypto']
    search_fields = ['user__username', 'crypto__symbol']
    readonly_fields = ['max_quantity']

    # Include the custom form in the admin view
    form = PurchaseForm

    def quantity_in_dollars(self, obj=None):
        if obj and obj.crypto and obj.crypto.price:
            if obj.quantity:
                return obj.quantity * obj.crypto.price
        return None

    def max_quantity(self, obj=None):
        if obj and obj.crypto and obj.crypto.price and obj.dollar_amount:
            return obj.dollar_amount / obj.crypto.price
        return None

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('dollar_amount') and obj.crypto and obj.crypto.price:
            dollar_amount = form.cleaned_data['dollar_amount']
            obj.quantity = dollar_amount / obj.crypto.price
            obj.amount_usd = dollar_amount  # Set the amount_usd field
        super().save_model(request, obj, form, change)

    def buy_max_action(self, request, queryset):
        for purchase in queryset:
            purchase.quantity = self.max_quantity(purchase)
            purchase.save()

    buy_max_action.short_description = 'Buy Max'

    actions = [buy_max_action]

admin.site.register(CryptoPrice, CryptoPriceAdmin)
admin.site.register(Purchase, PurchaseAdmin)
