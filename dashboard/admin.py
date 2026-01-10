from django.contrib import admin
from . models import *

# Register your models here.
class KlineAdmin(admin.ModelAdmin):
    pass

# class WithdrawalAdmin(admin.ModelAdmin):
#     pass
    
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
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
# admin.site.register(Wallet)
admin.site.register(Profile)

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'balance_usd')  # Still uses user, but __str__ now shows full name
    list_filter = ('user',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')  # Expanded search fields
    actions = ['update_usd_balances']

from django_celery_beat.models import PeriodicTask, IntervalSchedule

# from django.contrib import admin
# from django.urls import path
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import user_passes_test
# from django.core.mail import send_mass_mail
# from django.contrib import messages
# from .forms import EmailUsersForm
# from django.contrib.auth import get_user_model

# User = get_user_model()

# @admin.register(User)
# class CustomUserAdmin(admin.ModelAdmin):
#     # Add a custom link in the admin
#     change_list_template = "admin/send_email_changelist.html"

#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('send-email/', self.admin_site.admin_view(self.send_email_view), name='send-email-users'),
#         ]
#         return custom_urls + urls

#     def send_email_view(self, request):
#         if request.method == 'POST':
#             form = EmailUsersForm(request.POST)
#             if form.is_valid():
#                 subject = form.cleaned_data['subject']
#                 message = form.cleaned_data['message']
#                 from_email = None  # Uses DEFAULT_FROM_EMAIL
#                 recipient_list = list(User.objects.values_list('email', flat=True))

#                 if recipient_list:
#                     datatuple = [(subject, message, from_email, [email]) for email in recipient_list]
#                     send_mass_mail(datatuple, fail_silently=False)
#                     messages.success(request, f"Email sent to {len(recipient_list)} users.")
#                 else:
#                     messages.warning(request, "No users found to send email.")
#                 return redirect("..")
#         else:
#             form = EmailUsersForm()
#         return render(request, "admin/send_email_form.html", {"form": form})

from django.contrib import admin
from django.core.mail import send_mail
from .models import EmailSender

@admin.register(EmailSender)
class EmailSenderAdmin(admin.ModelAdmin):
    list_display = ['subject', 'created_at']
    actions = ['send_email_to_receivers']

    @admin.action(description="Send email to selected users")
    def send_email_to_receivers(self, request, queryset):
        for email_instance in queryset:
            subject = email_instance.subject
            message = email_instance.message
            receivers = email_instance.receivers.all()

            for user in receivers:
                if user.email:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email='ssmartmine@gmail.com',  # Set your email here
                        recipient_list=[user.email],
                        fail_silently=False,
                    )

        self.message_user(request, "Emails sent successfully.")
