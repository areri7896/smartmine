from django.db import models
from django.contrib.auth.models import User

class Trade(models.Model):
    SIDE_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=20)  # e.g., BTC/USD
    side = models.CharField(max_length=4, choices=SIDE_CHOICES)
    amount = models.DecimalField(max_digits=20, decimal_places=8)  # Crypto amount
    price = models.DecimalField(max_digits=20, decimal_places=8)   # Price at execution
    total = models.DecimalField(max_digits=20, decimal_places=2)   # USD Total
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.side} {self.amount} {self.symbol} @ {self.price}"
