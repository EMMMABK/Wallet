from django import forms
from django.contrib import admin
from .models import CryptoPrice, Purchase, Sales, SalesDollars
import requests
from django.urls import path
from django.db.models import Sum


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

class SalesForm(forms.ModelForm):
    class Meta:
        model = Sales
        fields = ['user', 'crypto', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        purchased_cryptos = Purchase.objects.values_list('crypto__id', flat=True).distinct()
        self.fields['crypto'].queryset = CryptoPrice.objects.filter(id__in=purchased_cryptos)


class SalesAdmin(admin.ModelAdmin):
    list_display = ['user', 'crypto', 'quantity', 'timestamp']
    list_filter = ['user', 'crypto']
    search_fields = ['user__username', 'crypto__symbol']

    form = SalesForm

    def save_model(self, request, obj, form, change):
        if obj.crypto and obj.quantity:
            # Check if the requested quantity exceeds the available purchased quantity
            purchased_quantity = Purchase.objects.filter(
                user=obj.user,
                crypto=obj.crypto
            ).aggregate(total_quantity=Sum('quantity'))['total_quantity']  # Use the Sum aggregation function

            if not purchased_quantity:
                purchased_quantity = 0

            remaining_quantity = purchased_quantity - obj.quantity

            if remaining_quantity < 0:
                raise forms.ValidationError(
                    f"Cannot sell more than the purchased quantity ({purchased_quantity})."
                )

            # Update the quantity in the Purchase model
            latest_purchase = Purchase.objects.filter(
                user=obj.user,
                crypto=obj.crypto
            ).order_by('timestamp').first()

            latest_purchase_quantity = latest_purchase.quantity

            if remaining_quantity == 0:
                latest_purchase.delete()
            else:
                latest_purchase.quantity = remaining_quantity
                latest_purchase.save()

            # Save the Sales object
            obj.save()

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial['user'] = request.user.id
        return initial


class SalesDollarsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit the queryset of 'crypto' field to only show available cryptocurrencies in Purchases
        purchased_cryptos = Purchase.objects.values_list('crypto__id', flat=True).distinct()
        self.fields['crypto'].queryset = CryptoPrice.objects.filter(id__in=purchased_cryptos)

    class Meta:
        model = SalesDollars
        fields = ['user', 'crypto', 'price']

    def clean(self):
        cleaned_data = super().clean()
        crypto = cleaned_data.get('crypto')
        price = cleaned_data.get('price')

        if not crypto or not price:
            return

        # Get the total purchased quantity
        purchased_quantity = Purchase.objects.filter(
            user=cleaned_data['user'],
            crypto=crypto
        ).aggregate(total_quantity=Sum('quantity'))['total_quantity']

        if not purchased_quantity:
            purchased_quantity = 0

        # Calculate the total purchased amount
        total_purchased_amount = purchased_quantity * crypto.price

        if total_purchased_amount < price:
            raise forms.ValidationError(
                f"Cannot sell for more than the total purchased amount ({total_purchased_amount})."
            )

        # Calculate the quantity to be deducted from Purchases
        quantity_to_deduct = price / crypto.price

        # Update the quantity in the Purchase model
        latest_purchase = Purchase.objects.filter(
            user=cleaned_data['user'],
            crypto=crypto
        ).order_by('timestamp').first()

        latest_purchase_quantity = latest_purchase.quantity

        remaining_quantity = latest_purchase_quantity - quantity_to_deduct

        if remaining_quantity == 0:
            latest_purchase.delete()
        else:
            latest_purchase.quantity = remaining_quantity
            latest_purchase.save()

        return cleaned_data

class SalesDollarsAdmin(admin.ModelAdmin):
    list_display = ['user', 'crypto', 'price', 'timestamp']
    list_filter = ['user', 'crypto']
    search_fields = ['user__username', 'crypto__symbol']

    form = SalesDollarsForm

admin.site.register(SalesDollars, SalesDollarsAdmin)
admin.site.register(Sales, SalesAdmin)
admin.site.register(CryptoPrice, CryptoPriceAdmin)
admin.site.register(Purchase, PurchaseAdmin)
