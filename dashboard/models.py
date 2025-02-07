from django.db import models

# Create your models here.
class Kline(models.Model):
    pair = models.CharField(max_length=30, default= 'BTCUSDC')
    open_time = models.DateTimeField()
    close_time = models.DateTimeField()
    open_amount = models.DecimalField(decimal_places=50, max_digits=200)
    high = models.DecimalField(decimal_places=50, max_digits=200)
    low = models.DecimalField(decimal_places=50, max_digits=200)
    close_amount = models.DecimalField(decimal_places=50, max_digits=200)


class MpesaCallback(models.Model):
    merchant_request_id = models.CharField(max_length=255, unique=True)
    checkout_request_id = models.CharField(max_length=255, unique=True)
    response_code = models.CharField(max_length=10)
    response_description = models.TextField()
    result_code = models.CharField(max_length=10)
    result_desc = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.merchant_request_id} - {self.result_desc}"
