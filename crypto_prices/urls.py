from django.urls import path
from .views import save_crypto_prices, buy_crypto

urlpatterns = [
    path('save_crypto_prices/', save_crypto_prices, name='save_crypto_prices'),
    path('buy_crypto/<int:user_id>/<str:symbol>/', buy_crypto, name='buy_crypto'),
]
