from django.contrib import admin
from . models import *

# Register your models here.
class KlineAdmin(admin.ModelAdmin):
    pass

# class WithdrawalAdmin(admin.ModelAdmin):
#     pass
    
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'amount', 'is_completed', 'created_at')
    # list_filter = ('is_completed')
    search_fields = ('user__username', 'phone_number')

class Depo_VerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'verification_code', 'amount', 'is_completed', 'created_at')
    # list_filter = ('is_completed')
    search_fields = ('user__username', 'phone_number')


admin.site.register(Kline, KlineAdmin)
admin.site.register(Withdrawal, WithdrawalAdmin)
admin.site.register(Depo_Verification,Depo_VerificationAdmin)
admin.site.register(Investment)
admin.site.register(InvestmentPlan)
admin.site.register(MpesaCallback)
admin.site.register(Wallet)
admin.site.register(Profile)

from django_celery_beat.models import PeriodicTask, IntervalSchedule
