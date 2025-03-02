from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta

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

# class InvestmentPlan(models.Model):
#     user = 
#     name = models.Charfield(max_length = 50)
#     daily_interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
#     available_balance = models.DecimalField(max_digits=5, decimal_places=2)
#     purchase_limit = models.CharField(max_length = 100, default="no restrictions")
#     purchase_quantity = models.IntegerField(default=1)
#     rate = 
#     cycle_days = 
#     price = 


class InvestmentPlan(models.Model):
    PLAN_CHOICES = [
        ("AMATUER", "AMATUER"),
        ("BEGINNER", "BEGINNER"),
        ("INTERMIDIATE", "INTERMIDIATE"),
        ("LEGENDARY", "LEGENDARY"),
        ("PRO", "PRO"),
    ]

    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(max_length = 100, null=True)
    daily_interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Stored as 2.30 for 2.3%
    cycle_days = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.price} USDT"

class Investment(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(InvestmentPlan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    def calculate_earnings(self):
        return self.plan.price * (self.plan.daily_interest_rate / 100) * self.plan.cycle_days

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"
