from django.test import TestCase
from django.contrib.auth import authenticate
from .models import User, Profile, Account, Transfer, Transaction
from datetime import datetime, timedelta, tzinfo
import pytz
#
# class AccountTest(TestCase):
#     tz = pytz.timezone("Australia/Sydney")
#     today = tz.localize(datetime.today())
#
#     user = User.objects.create(username="testuser", password="testA")
#     usr_from = User.objects.create(username="fromuser", password="testB")
#     usr_to = User.objects.create(username="touser", password="testC")
#
#     acc = Account.objects.create(user=self.user)
#     acc_from = Account.objects.create(user=self.usr_from)
#     acc_to = Account.objects.create(user=self.usr_to)
#
#     tx_from = Transaction.objects.create(transaction_type='w', title="transaction1", account=self.acc_from, value="-10.50", created_at=self.today, modified_at=self.today, confirmed_at=self.today)
#     tx_to = Transaction.objects.create(transaction_type='d', title="transaction1", account=self.acc_to, value="10.50", created_at=self.today, modified_at=self.today, confirmed_at=self.today)
#
#     def setUp(self):
#         # Make basic payment.
#         Transfer.objects.create(tx_from=self.tx_from, tx_to=self.tx_to, deadline=self.today)
#
#         # Make basic request.
#         Transfer.objects.create(tx_from=self.tx_from._copy(), tx_to=self.tx_to._copy(), deadline=self.today, is_request=True)
#
#     def test_balance(self):
#         self.assertEqual(self.acc.balance, 0)
#         self.assertEqual(self.usr_to.balance, 10.5000)
#
#     def test_num_payments(self):
#         self.assertEqual(self.acc.num_payments, 0)
#         self.assertEqual(self.acc_from.num_payments, 1)
#
#     def test_num_requests(self):
#         # TODO
#         return True
#
#     def test_num_groups(self):
#         # TODO
#         return True
#
#     def test_deposit(self):
#         # TODO
#         return True
#
#     def test_withdraw(self):
#         # TODO
#         return True
#
#     def test_approve_req(self):
#         # TODO
#         return True
#
#     def test_delete_transfer(self):
#         # TODO
#         return True
#
#     def test_create_transaction(self):
#         # TODO
#         return True
#
#     def test_create_transfer(self):
#         # TODO
#         return True
#
#     def test_str(self):
#         # TODO
#         return True

class GroupAccountTest(TestCase):
    def test_str(self):
        # TODO
        return True

class ProfileModelTest(TestCase):
    name = "test-user"
    pw = "test"

    def test_str(self):
        user = User.objects.create(username=self.name, password=self.pw)
        p = Profile.objects.create(user=user, avatar=None)
        self.assertEqual(str(p), "@"+self.name)

class TransactionModelTest(TestCase):
    tz = pytz.timezone("Australia/Sydney")
    today = tz.localize(datetime.today())

    def setUp(self):
        usr_from = User.objects.create(username="from", password="test")
        usr_to = User.objects.create(username="to", password="test")
        acc_from = Account.objects.create(user=usr_from)
        acc_to = Account.objects.create(user=usr_to)

        tx_from = Transaction.objects.create(transaction_type='w', title="testfrom", account=acc_from, value="-10.50", created_at=self.today, modified_at=self.today)
        tx_to = Transaction.objects.create(transaction_type='d', title="testto", account=acc_to, value="10.50", created_at=self.today, modified_at=self.today)

    def test_str(self):
        # TODO
        return True

    def test_copy(self):
        # TODO
        return True

    def test_notify(self):
        # TODO
        return True


    def test_notify(self):
        # TODO
        return True

class TransferModelTest(TestCase):
    tz = pytz.timezone("Australia/Sydney")
    today = tz.localize(datetime.today())

    def setUp(self):
        usr_from = User.objects.create(username="from", password="test")
        usr_to = User.objects.create(username="to", password="test")
        acc_from = Account.objects.create(user=usr_from)
        acc_to = Account.objects.create(user=usr_to)

        tx_from = Transaction.objects.create(transaction_type='w', title="testfrom", account=acc_from, value="-10.50", created_at=self.today, modified_at=self.today)
        tx_to = Transaction.objects.create(transaction_type='d', title="testto", account=acc_to, value="10.50", created_at=self.today, modified_at=self.today)

        Transfer.objects.create(tx_from=tx_from, tx_to=tx_to, deadline=self.today)

    def test_str(self):
        transfer = Transfer.objects.get(id="1")
        self.assertEqual(str(transfer), "from-- $10.5000 -->to")

    def test_delete(self):
        transfer = Transfer.objects.get(id="1")
        transfer.delete()
        self.assertTrue(transfer.tx_from.is_deleted)
        self.assertTrue(transfer.tx_to.is_deleted)
        self.assertTrue(transfer.is_deleted)

    def test_confirm_not_recurr(self):
        transfer = Transfer.objects.get(id="1")
        transfer.confirm(self.today)
        self.assertEqual(transfer.confirmed_at, self.today)
        self.assertEqual(transfer.tx_from.confirmed_at, self.today)
        self.assertEqual(transfer.tx_to.confirmed_at, self.today)
        self.assertFalse(transfer.tx_from.is_pending)
        self.assertFalse(transfer.tx_to.is_pending)
        # Check that no copy has been made.
        self.assertTrue(len(Transfer.objects.all()) < 2)

    def test_confirm_recurr(self):
        today = datetime.today()
        transfer = Transfer.objects.get(id="1")
        transfer.recurrence_days = 7
        transfer.save()
        transfer.confirm(self.today)
        self.assertEqual(transfer.confirmed_at, self.today)
        self.assertEqual(transfer.tx_from.confirmed_at, self.today)
        self.assertEqual(transfer.tx_to.confirmed_at, self.today)
        self.assertFalse(transfer.tx_from.is_pending)
        self.assertFalse(transfer.tx_to.is_pending)
        # Check that no copy has been made.
        self.assertIsNotNone(Transfer.objects.get(id="2"))

    def test_recurring_copy(self):
        tz = pytz.timezone("Australia/Sydney")
        now = datetime.now()
        today = tz.localize(now)
        new_deadline = today + timedelta(days=7)
        transfer = Transfer.objects.get(id="1")
        transfer.recurrence_days = 7
        transfer.save()
        transfer.create_recurring_copy(today)

        recurr = Transfer.objects.get(id="2")
        self.assertIsNotNone(recurr)
        self.assertEqual(recurr.recurrence_days, 7)
        self.assertEqual(recurr.is_request, transfer.is_request)
        self.assertEqual(recurr.deadline.strftime("%Y-%m-%d"), new_deadline.strftime("%Y-%m-%d"))

        self.assertEqual(recurr.tx_from.account, transfer.tx_from.account)
        self.assertEqual(recurr.tx_from.value, transfer.tx_from.value)
        self.assertEqual(recurr.tx_from.title, transfer.tx_from.title)
        self.assertEqual(recurr.tx_from.transaction_type, 'w')
        self.assertEqual(recurr.tx_from.modified_at.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
        self.assertIsNone(recurr.tx_from.confirmed_at)

        self.assertEqual(recurr.tx_to.account, transfer.tx_to.account)
        self.assertEqual(recurr.tx_to.value, transfer.tx_to.value)
        self.assertEqual(recurr.tx_to.title, transfer.tx_to.title)
        self.assertEqual(recurr.tx_to.transaction_type, 'd')
        self.assertEqual(recurr.tx_to.modified_at.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
        self.assertIsNone(recurr.tx_to.confirmed_at)


    def test_notify(self):
        # TODO test email notification
        return True
