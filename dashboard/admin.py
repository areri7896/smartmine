from django.contrib import admin
from . models import *

# Register your models here.
class KlineAdmin(admin.ModelAdmin):
    pass

admin.site.register(Kline, KlineAdmin)
admin.site.register(Investment)
admin.site.register(InvestmentPlan)
admin.site.register(MpesaCallback)