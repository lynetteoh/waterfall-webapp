from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMessage
from django.db import models, transaction
from django.contrib.auth.models import User
from webapp.models import Profile, Account, Transaction, Transfer

from datetime import datetime, timedelta
import pytz

# Updates various transactions in the database.
# Will be called by the Scheduler running in the background periodically.
class Command(BaseCommand):
    help = "Script updates any pending recurring transactions."

    @transaction.atomic
    def handle(self, *args, **options):
        pending_transfers = Transfer.objects.select_for_update()\
                                            .filter(is_deleted=False,\
                                                    confirmed_at__isnull=True)
        for t in pending_transfers:
            timezone = pytz.timezone('Australia/Sydney')
            today = timezone.localize(datetime.today()).date()

            # Check for missed deadlines & notification requirements.
            if t.deadline and t.deadline.date() == (timedelta(days=3) + today):
                self.stdout.write("...Reminding pending transfer %d." % t.id)
                subj = "Reminder: Recurring TricklePay in 3 Days"
                template = "email/reminder-recurr.html"
                if t.is_request:
                    subj = "Reminder: TricklePay Request Deadline in 3 Days"
                    template = "email/reminder-req.html"

                # Attempt to send email notification
                try:
                    t = threading.Thread(target=t.notify, args=(subj, template,))
                    t.start()
                except Exception as e:
                    print("Failed to send mail: " + str(e))
                continue

            # Delete failed payments and requests.
            elif t.deadline and (t.deadline.date() < today):
                self.stdout.write("...Deleting pending transfer %d." % t.id)
                t.delete()
                subj = "Cancelled Recurring TricklePay"
                template = "email/failed-recurr.html"
                if t.is_request:
                    subj = "TricklePay Request Expired"
                    template = 'email/failed-req.html'

                # Attempt to send email notification
                try:
                    t = threading.Thread(target=t.notify, args=(subj, template,))
                    t.start()
                except Exception as e:
                    print("Failed to send mail: " + str(e))
                continue

            # Ignore requests as they can only be accepted by a user.
            if t.deadline and (t.deadline.date() > today) and t.is_request:
                continue
            self.stdout.write("...Updating pending transfer %d." % t.id)
            tx_from = Transaction.objects.filter(id=t.tx_from.id).select_for_update().first()
            tx_to = Transaction.objects.filter(id=t.tx_to.id).select_for_update().first()

            # Check balances and delete recurring payments with insufficent funds.
            w_tx = tx_from if (tx_from.transaction_type is 'w') else tx_to
            if (w_tx.account.balance < w_tx.value):
                continue        # as it will be auto deleted tomorrow

            t.confirm(timezone.localize(datetime.now()))
        return
