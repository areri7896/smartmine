from django.utils.timezone import now
from .models import Investment
import logging

logger = logging.getLogger(__name__)


def process_daily_profits():
    """
    Process daily profits for all active investments.
    Should run once per day via cron job.
    """
    today = now().date()
    
    # Find investments that need profit payment
    investments = Investment.objects.filter(
        status="active",
        start_date__lte=now(),
        last_profit_date__lt=today
    ).select_related('user', 'plan') | Investment.objects.filter(
        status="active",
        start_date__lte=now(),
        last_profit_date__isnull=True
    ).select_related('user', 'plan')
    
    logger.info(f"Processing {investments.count()} investments for daily profit")
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for investment in investments:
        try:
            if investment.process_daily_profit():
                success_count += 1
            else:
                skipped_count += 1
        except Exception as e:
            error_count += 1
            logger.error(f"Failed to process investment {investment.id}: {e}")
    
    logger.info(
        f"Daily profit processing complete. "
        f"Success: {success_count}, Skipped: {skipped_count}, Errors: {error_count}"
    )


# Legacy function name for backward compatibility
def daily_profit():
    """Legacy function - calls new process_daily_profits()"""
    process_daily_profits()