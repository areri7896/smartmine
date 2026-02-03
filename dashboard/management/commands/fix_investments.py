from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.db import transaction
from django.core.mail import send_mail
from dashboard.models import Investment, Wallet, Transaction, InvestmentPlan

class Command(BaseCommand):
    help = 'Apply fixes to investments: payout expired ones and fix complete but unpaid ones'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting investment fix process...')
        
        try:
            # 1. Update status based on time (Active -> Completed, with Payout)
            self.update_investment_status()
            self.stdout.write('update_investment_status() executed.')
            
            # 2. Fix investments that are already "completed" but funds were not returned
            self.process_investments()
            self.stdout.write('process_investments() executed.')
            
            self.stdout.write(self.style.SUCCESS('Successfully applied investment fixes.'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error applying fixes: {e}'))

    def update_investment_status(self):
        investments = Investment.objects.filter(status="active", end_date__lte=now())
        for investment in investments:
            try:
                investment.complete_investment()
                self.stdout.write(f"Completed investment {investment.id}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error completing investment {investment.id}: {e}"))

    def process_investments(self):
        # Look for status="completed"
        investments = Investment.objects.filter(status="completed")

        for inv in investments:
            try:
                with transaction.atomic():
                    # Check if already paid
                    if inv.total_payout > 0 or inv.status == "paid":
                        continue

                    self.stdout.write(f"Processing unpaid completed investment {inv.id}...")

                    # Lock wallet
                    wallet = Wallet.objects.select_for_update().get(user=inv.user)
                    
                    # Payout only capital (profit is paid daily)
                    capital = inv.plan.price
                    wallet.balance += capital
                    wallet.save()

                    inv.total_payout = capital + inv.total_profit_paid
                    inv.status = "paid"
                    inv.completed_at = now()
                    inv.save()

                    # Record transaction
                    Transaction.objects.create(
                        user=inv.user,
                        wallet=wallet,
                        transaction_type='investment',
                        amount=capital,
                        reference_id=f"INV-{inv.id}-CAPITAL-RETURN-FIX",
                        status='success'
                    )

                    # Send email
                    send_mail(
                        subject="Your Investment Has Matured!",
                        message=f"Your investment in {inv.plan.name} has been fully paid out.\n"
                                f"Total earned: {inv.total_profit_paid} + Capital: {capital}.",
                        from_email="info@smrtmine.com",
                        recipient_list=[inv.user.email],
                        fail_silently=True,
                    )
                    self.stdout.write(f"Successfully processed payout for investment {inv.id}")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing investment payout {inv.id}: {e}"))
