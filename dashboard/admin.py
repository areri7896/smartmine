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
@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = (
        'user', 
        'plan', 
        'principal_amount', 
        'status', 
        'start_date', 
        'end_date', 
        'days_profit_paid', 
        'total_profit_paid'
    )
    list_filter = ('status', 'plan', 'start_date', 'end_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'plan__name')
    actions = ['trigger_daily_profit', 'force_complete_investment']

    @admin.action(description="Trigger Daily Profit for Selected Investments")
    def trigger_daily_profit(self, request, queryset):
        success_count = 0
        skipped_count = 0
        error_count = 0
        
        for investment in queryset:
            try:
                if investment.process_daily_profit():
                    success_count += 1
                else:
                    skipped_count += 1
            except Exception as e:
                error_count += 1
                self.message_user(
                    request, 
                    f"Error processing investment {investment.id}: {str(e)}", 
                    level='ERROR'
                )
        
        self.message_user(
            request,
            f"Profit Processing: {success_count} success, {skipped_count} skipped, {error_count} errors."
        )

    @admin.action(description="Force Complete Selected Investments")
    def force_complete_investment(self, request, queryset):
        success_count = 0
        error_count = 0
        
        for investment in queryset:
            try:
                investment.complete_investment()
                success_count += 1
            except Exception as e:
                error_count += 1
                self.message_user(
                    request, 
                    f"Error completing investment {investment.id}: {str(e)}", 
                    level='ERROR'
                )
        
        self.message_user(
            request, 
            f"Completion Processing: {success_count} completed, {error_count} errors."
        )

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

@admin.register(SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'ip_address', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'ip_address', 'details')
    readonly_fields = ('user', 'action', 'ip_address', 'user_agent', 'details', 'timestamp')


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('usd_to_kes', 'is_active', 'updated_at', 'note')
    list_filter = ('is_active',)
    list_editable = ('is_active',)
    readonly_fields = ('updated_at',)
    ordering = ('-updated_at',)

    def save_model(self, request, obj, form, change):
        """
        When a new active rate is saved, deactivate all other rates
        to enforce the singleton constraint.
        """
        if obj.is_active:
            ExchangeRate.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)
