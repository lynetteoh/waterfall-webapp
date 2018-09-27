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

    # @transaction.atomic
    def handle(self, *args, **options):
        pending_transfers = Transfer.objects.select_for_update()\
                                            .filter(is_request=False,\
                                                    is_deleted=False,\
                                                    confirmed_at__isnull=True)
        for t in pending_transfers:
            # See if transfer can be executed or should be deleted.
            timezone = pytz.UTC     # TODO get user timezone
            today = timezone.localize(datetime.today()).date()

            if t.deadline and t.deadline.date() == (timedelta(days=3) + today):
                self.stdout.write("...Reminding pending transfer %d." % t.id)
                self.notify(t, True)
                continue
            elif t.deadline and (t.deadline.date() < today):
                self.stdout.write("...Deleting pending transfer %d." % t.id)
                t.delete()
                self.notify(t, False)
                continue
            elif t.deadline and (t.deadline.date() > today):
                continue

            self.stdout.write("...Updating pending transfer %d." % t.id)
            tx_from = Transaction.objects.filter(id=t.tx_from.id).select_for_update().first()
            tx_to = Transaction.objects.filter(id=t.tx_to.id).select_for_update().first()
            # Check balances.
            w_tx = tx_from if (tx_from.transaction_type is 'w') else tx_to
            if (w_tx.account.balance < w_tx.value):
                continue

            t.confirm(timezone.localize(datetime.now()))
        return

    # Sends email notification.
    def notify(self, transfer, is_reminder):
        print("TODO: Notification")
        return
        # Ensure that tx_from is the payer and tx_to the payee.
        tx_from = transfer.tx_from
        tx_to   = transfer.tx_to
        if (tx_from.transaction_type is not 'w'):
            tx_from, tx_to = tx_to, tx_from
        acc_from = Account.objects.filter(id=tx_from.account).select_for_update()
        acc_to = Account.objects.filter(id=tx_to.account).select_for_update()

        # Get email templates, format with the right fields and send mail.
        if (is_reminder):
            subj, body = reminder_template()
        else:
            subj, body = delete_template()
        body_from = body.format(amount, "to " + acc_to.username, acc_from.balance)
        body_to   = body.format(amount, "from " + acc_from.username, acc_to.balance)
        EmailMessage(subj, body_from, acc_from.email).send()
        EmailMessage(subj, body_to, acc_to.email).send()

    # Email notification about a failed recurring transfer.
    def delete_template():
        subj = "A recurring TricklePay has been cancelled"
        body = """This is an automated email notification.
                   Due to insufficient funds in your Waterfall balance we have \
                   cancelled your recurring payment of $%f %s due today.
                   Your Waterfall balance still remains as $%f."""
        return (subj, body)

    # Email notification about a recurring transfer payment.
    def reminder_template():
        subj = "Reminder: Recurring TricklePay in 3 Days"
        body = """This is an automated email notification.
                   We would like to remind you that a recurring TricklePay \
                   transfer of $%f %s is due in 3 days.
                   Your Waterfall balance is currently $%f."""
        return (subj, body)
