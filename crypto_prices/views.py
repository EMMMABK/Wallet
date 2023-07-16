import requests
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from .models import CryptoPrice, Purchase

def save_crypto_prices(request):
    response = requests.get('https://api.binance.com/api/v3/ticker/price')
    data = response.json()
    
    for item in data:
        symbol = item['symbol']
        price = item['price']
        
        CryptoPrice.objects.create(symbol=symbol, price=price)
    
    return HttpResponse('Crypto prices saved successfully.')

def buy_crypto(request, user_id, symbol):
    try:
        user = User.objects.get(pk=user_id)
        crypto = CryptoPrice.objects.get(symbol=symbol)
        user_balance = 1000  # Set the user's balance here (in this example, it's 1000 USD)

        # Calculate the maximum quantity of crypto the user can buy
        max_quantity = user_balance / crypto.price

        # Save the purchase in the Cart (Purchase model)
        Purchase.objects.create(user=user, crypto=crypto, quantity=max_quantity)

        return JsonResponse({'message': f'Successfully bought {max_quantity} {symbol}'})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except CryptoPrice.DoesNotExist:
        return JsonResponse({'error': 'Crypto not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
