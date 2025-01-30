from django.contrib import admin
from . models import Subscriber

# Register your models here.
# class Subscriber(admin.ModelAdmin):
#     pass

admin.site.register(Subscriber)