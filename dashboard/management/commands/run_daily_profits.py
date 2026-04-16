from django.core.management.base import BaseCommand
from dashboard.cron import process_daily_profits
import logging

class Command(BaseCommand):
    help = 'Process daily profits for all active investments'

    def handle(self, *args, **options):
        self.stdout.write('Starting daily profit processing...')
        
        try:
            # Re-use the logic from cron.py
            process_daily_profits()
            self.stdout.write(self.style.SUCCESS('Successfully processed daily profits'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing profits: {str(e)}'))
