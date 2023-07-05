from django.contrib import admin
from .models import CryptoPrice
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

admin.site.register(CryptoPrice, CryptoPriceAdmin)