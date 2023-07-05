from django.urls import path
from crypto_prices.views import save_crypto_prices

urlpatterns = [
    path('save-crypto-prices/', save_crypto_prices, name='save_crypto_prices'),
]
