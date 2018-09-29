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
            timezone = pytz.UTC     # TODO get user timezone
            today = timezone.localize(datetime.today()).date()

            # Check for missed deadlines & notification requirements.
            if t.deadline and t.deadline.date() == (timedelta(days=3) + today):
                self.stdout.write("...Reminding pending transfer %d." % t.id)
                template = self.reminder_recurr_template()
                if t.is_request:
                    template = self.reminder_req_template()
                self.notify(t, template)
                continue
            elif t.deadline and (t.deadline.date() < today):
                self.stdout.write("...Deleting pending transfer %d." % t.id)
                t.delete()
                template = self.delete_recurr_template()
                if t.is_request:
                    template = self.delete_req_template()
                self.notify(t, template)
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

    # Sends email notification.
    def notify(self, transfer, template):
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
        subj, body = template
        body_from = body.format(amount, "to " + acc_to.username, acc_from.balance)
        body_to   = body.format(amount, "from " + acc_from.username, acc_to.balance)
        EmailMessage(subj, body_from, acc_from.email).send()
        EmailMessage(subj, body_to, acc_to.email).send()

    # Email notification about a failed recurring transfer.
    def delete_recurr_template(self):
        subj = "A recurring TricklePay has been cancelled"
        body = """This is an automated email notification.
                   Due to insufficient funds in your Waterfall balance we have \
                   cancelled your recurring payment of $%f %s due today.
                   Your Waterfall balance still remains as $%f."""
        return (subj, body)

    # Email notification about a failed request transfer.
    def delete_req_template(self):
        subj = "A TricklePay Request has been cancelled"
        body = """This is an automated email notification.
                   We have cancelled your TricklePay request of $%f %s as it \
                   has passed the request deadline.
                   Your Waterfall balance still remains as $%f."""
        return (subj, body)

    # Email notification about a recurring transfer payment.
    def reminder_recurr_template(self):
        subj = "Reminder: Recurring TricklePay in 3 Days"
        body = """This is an automated email notification.
                   We would like to remind you that a recurring TricklePay \
                   transfer of $%f %s is due in 3 days.
                   Your Waterfall balance is currently $%f."""
        return (subj, body)

    # Email notification about a recurring transfer payment.
    def reminder_req_template(self):
        subj = "Reminder: TricklePay Request Deadline is in 3 Days"
        body = """This is an automated email notification.
                   We would like to remind you that a TricklePay request for a \
                   transfer of $%f %s is due in 3 days.
                   Your Waterfall balance is currently $%f."""
        return (subj, body)
