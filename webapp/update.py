from datetime import datetime, timedelta
from django.core.mail import EmailMessage
from django.db import models, transaction
from django.contrib.auth.models import User
from .models import Profile, Account, Transaction, OneToOnePayment

# Updates various transactions in the database.
# Will be called by the Scheduler running in the background periodically.
@transaction.atomic
def update():
    # Traverse through the database and look for pending transfers.
    pending_transfers = Transfer.objects.select_for_update()
                                        .filter(is_request=False,
                                                is_deleted=False,
                                                confirmed_at__isnull=False)
    to_delete = []
    for t in pending_transfers:
        # See if transfer can be executed or should be deleted.
        today = datetime.today()
        if (t.deadline is timedelta(days=3) + now):
            notify(t, True)
        elif (t.deadline > now):
            t.delete()
            notify(t, False)
        elif (t is not now):
            continue

        tx_from = Transaction.objects.filter(id=t.tx_from.id).select_for_update()
        tx_to = Transaction.objects.filter(id=t.tx_to.id).select_for_update()

        # Check balances.
        w_tx = tx_from.transaction_type is 'w' ? tx_from : tx_to
        if (w_tx.account.balance < w_tx.value):
            continue

        t.confirm_recurring(today)
    return

# Sends email notification.
def notify(transfer, is_reminder):
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
