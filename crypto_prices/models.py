
from django.contrib.auth.models import User
from django.db import models

class CryptoPrice(models.Model):
    symbol = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.symbol

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    crypto = models.ForeignKey(CryptoPrice, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def dollar_amount(self):
        if self.crypto and self.crypto.price and self.quantity:
            return self.quantity * self.crypto.price
        return None

    def __str__(self):
        return f'{self.user.username} - {self.crypto.symbol} - {self.quantity}'

class Sales(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    crypto = models.ForeignKey(CryptoPrice, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.crypto.symbol} - {self.quantity}'

class SalesDollars(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    crypto = models.ForeignKey(CryptoPrice, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.crypto.symbol} - {self.price}'
