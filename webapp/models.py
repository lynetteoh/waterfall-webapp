from django.db import models, transaction
from django.db.models import Sum
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import os, pytz

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/avatars/user_<id>/<filename>
    return 'avatars/{0}/{1}'.format(instance.user.id, filename)

class Profile(models.Model):
    import pytz
    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=user_directory_path, height_field=None, width_field=None)
    timezone = models.CharField(max_length=32, choices=TIMEZONES, default='UTC')
    # balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return '@{}'.format(self.user.username)

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def register_deposit(self, title, value):
        return self._create_transaction(value, title, 'd', False)

    def register_withdrawal(self, title, value):
        if self.balance >= value:
            return self._create_transaction(0-value, title, 'w', False)
        else:
            print('Account funds are insufficient.')
            return None

    def approve_req(self, transfer):
        if (not transfer.is_request)\
            or transfer.is_deleted or transfer.confirmed_at:
            return "Invalid Transfer"

        # Check request needs a withdrawal from self and sufficient balance.
        tx = transfer.tx_to
        if tx.account is not self:
            return "Incorrect Request"
        if tx.amount > self.balance:
            return "Insufficient Funds"

        # Approve request and make recurring repeats if needed.
        now = pytz.UTC.localize(datetime.now())
        transfer.confirm(now, True)
        print ("Request successfully approved.")
        return "Success"

    def delete_transfer(self, transfer):
        if transfer.confirmed_at:
            return "Past Transfer Cannot be Cancelled"

        if transfer.is_request:
            if transfer.tx_to.account is not self:
                return "User does not control Request"
        else:
            if transfer.tx_from.account is not self:
                return "User does not control Transfer"

        # Approve request and make recurring repeats if needed.
        transfer.delete()
        print ("Request successfully deleted.")
        return "Success"

    def _create_transaction(self, value, title, type, is_request):
        print("Created transaction " + type + " to " + self.user.username)
        now = None if is_request else pytz.UTC.localize(datetime.now())
        return Transaction.objects.create(
            account=self,
            title=title,
            value=value,
            transaction_type=type,
            confirmed_at=now,
        )

    def _create_transfer(self, receiver, subj, amount, recurr, date, is_request):
        # Reverse if it is a request.
        sender = self
        if is_request:
            sender, receiver = receiver, sender

        tx_sender = sender._create_transaction(0-amount, subj, 'w', is_request)
        tx_receiver = receiver._create_transaction(amount, subj,'d', is_request)

        today = pytz.UTC.localize(datetime.today()).date()
        today = pytz.UTC.localize(datetime.combine(today, datetime.min.time()), is_dst=True)
        date = pytz.UTC.localize(datetime.combine(date, datetime.min.time()), is_dst=True)
        confirmed_at = pytz.UTC.localize(datetime.now()) \
                            if (today == date and not is_request) else None
        pending = True if confirmed_at else False
        link_tx = Transfer.objects.create(
            tx_from = tx_sender,
            tx_to = tx_receiver,
            is_request = is_request,
            recurrence_days = recurr,
            deadline = date,
            confirmed_at = confirmed_at,
        )
        tx_sender.confirmed_at = confirmed_at
        tx_sender.is_pending = pending
        tx_sender.save()
        tx_receiver.confirmed_at = confirmed_at
        tx_receiver.is_pending = pending
        tx_receiver.save()
        link_tx.save()
        print("Created new transfer.")

        # Create recurring copy of transfer if it is a payment made today.
        if (not is_request and recurr and recurr > 0):
            link_tx.create_recurring_copy(today)
        return

    def __str__(self):
        return '@{}'.format(self.user.username)

    @property
    def balance(self):
        bal = Transaction.objects\
                    .filter(account=self, is_deleted=False, confirmed_at__isnull=False)\
                    .aggregate(Sum('value'))['value__sum']
        return bal if bal else 0

    @property
    def num_payments(self):
        num_payments = 0
        payments = Transfer.objects.filter(is_deleted=True,\
                                            confirmed_at__isnull=True)
        for p in payments:
            if p.tx_from.account == self.user.account:
                num_payments += 1
        return num_payments

    @property
    def num_requests(self):
        num_requests = 0
        requests = Transfer.objects.filter(is_deleted=True, is_request=True,\
                                    confirmed_at__isnull=True)
        for r in requests:
            if r.tx_from.account == self.user.account:
                num_requests += 1
        return num_requests

    @property
    def num_groups(self):
        # TODO Change this after implementing groups
        return 0

class Transaction(models.Model):
    TRANSACTION_TYPES = {
        'withdrawal': 'w',
        'deposit': 'd',
    }

    TRANSACTION_TYPE_CHOICES = [
        (TRANSACTION_TYPES['withdrawal'], 'withdrawal'),
        (TRANSACTION_TYPES['deposit'], 'deposit'),
    ]

    title = models.CharField(max_length=255)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    transaction_type = models.CharField(
        max_length=1,
        default='d',
        choices=TRANSACTION_TYPE_CHOICES,
    )

    value = models.DecimalField(max_digits=10, decimal_places=4)
    is_deleted = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} | @{} | ${}'.format(self.created_at, self.account.user.username, self.value)

    def _copy(self):
        return Transaction.objects.create(
            account=self.account,
            title=self.title,
            value=self.value,
            transaction_type=self.transaction_type,
            is_pending=self.is_pending,
            created_at=self.created_at,
            modified_at=self.modified_at,
            confirmed_at=self.confirmed_at,
        )

class Transfer(models.Model):
    tx_from = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='tx_from')
    tx_to = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='tx_to')

    recurrence_days = models.IntegerField(blank=True, null=True)
    is_request = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    deadline = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{}-- ${} -->{}'.format(self.tx_from.account.user.username, self.tx_to.value, self.tx_to.account.user.username)

    @transaction.atomic
    def delete(self):
        self.tx_from.is_deleted = True
        self.tx_to.is_deleted = True
        self.is_deleted = True
        self.tx_from.save()
        self.tx_to.save()
        self.save()

    @transaction.atomic
    def confirm(self, today):
        self.confirmed_at  = today
        self.save()
        self.tx_from.confirmed_at = today
        self.tx_from.is_pending   = False
        self.tx_from.save()
        self.tx_to.confirmed_at   = today
        self.tx_to.is_pending     = False
        self.tx_to.save()
        print("Transfer %d is confirmed." % self.id)

        # Create recurring copy of transfer.
        if (self.recurrence_days and self.recurrence_days > 0):
            self.create_recurring_copy(today)

    @transaction.atomic
    def create_recurring_copy(self, today):
        new_exec_date = today + timedelta(days=self.recurrence_days)
        tx_from_copy = self.tx_from._copy()
        tx_from_copy.created_at = self.tx_from.created_at
        tx_from_copy.modified_at = today
        tx_from_copy.confirmed_at = None
        tx_from_copy.save()

        tx_to_copy = self.tx_to._copy()
        tx_to_copy.created_at = self.tx_to.created_at
        tx_to_copy.modified_at = today
        tx_to_copy.confirmed_at = None
        tx_to_copy.save()

        Transfer.objects.create(
            tx_from=tx_from_copy,
            tx_to=tx_to_copy,
            deadline=new_exec_date,
            recurrence_days=self.recurrence_days,
            is_request=self.is_request,
        )
        print("Created recurring transfer copy.")
