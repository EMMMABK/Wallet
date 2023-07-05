import requests
from .models import CryptoPrice
from django.http import HttpResponse


def save_crypto_prices(request):
    response = requests.get('https://api.binance.com/api/v3/ticker/price')
    data = response.json()
    
    for item in data:
        symbol = item['symbol']
        price = item['price']
        
        CryptoPrice.objects.create(symbol=symbol, price=price)
    
    return HttpResponse('Crypto prices saved successfully.')
