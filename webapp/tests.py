from django.test import TestCase
from django.contrib.auth import authenticate
from django.core import mail
from .models import User, Profile, Account, Transfer, Transaction, GroupAccount
from datetime import datetime, timedelta, tzinfo
import pytz


class AccountTest(TestCase):
    tz = pytz.timezone("Australia/Sydney")
    today = tz.localize(datetime.today())

    def setUp(self):
        self.user = User.objects.create(username="testuser", password="testA")
        self.usr_from = User.objects.create(username="fromuser", password="testB")
        self.usr_to = User.objects.create(username="touser", password="testC")

        self.group = GroupAccount.objects.create(name="group", account=Account.objects.create())
        self.user.profile = Profile.objects.create(user=self.user)
        self.usr_from.profile = Profile.objects.create(user=self.usr_from)
        self.group.members.add(self.usr_from.profile)

        self.acc = Account.objects.create(user=self.user)
        self.acc_from = Account.objects.create(user=self.usr_from)
        self.acc_to = Account.objects.create(user=self.usr_to)
        self.acc_from.deposit(500)

        self.tx_from = Transaction.objects.create(transaction_type='w', title="transaction1", account=self.acc_from, value="-10.50", created_at=self.today, modified_at=self.today, confirmed_at=self.today)
        self.tx_to = Transaction.objects.create(transaction_type='d', title="transaction1", account=self.acc_to, value="10.50", created_at=self.today, modified_at=self.today, confirmed_at=self.today)

        # Make basic payment.
        self.pay = Transfer.objects.create(tx_from=self.tx_from, tx_to=self.tx_to, deadline=self.today, confirmed_at=self.today)

        # Make basic request.
        tx_from_copy = self.tx_from._copy()
        tx_to_copy   = self.tx_to._copy()
        tx_from_copy.confirmed_at = None
        tx_to_copy.confirmed_at = None
        tx_from_copy.save()
        tx_to_copy.save()
        self.req = Transfer.objects.create(tx_from=tx_from_copy, tx_to=tx_to_copy, deadline=self.today, is_request=True)

    def test_str(self):
        self.assertEqual(str(self.user.account), "@testuser")
        self.assertEqual(str(self.group.account), "group (Group)")

    def test_balance(self):
        self.assertEqual(self.acc.balance, 0)
        self.assertEqual(self.usr_to.account.balance, 10.5000)

    def test_num_payments(self):
        self.assertEqual(self.acc.num_payments, 0)
        self.assertEqual(self.acc_from.num_payments, 1)

    def test_num_requests(self):
        self.assertEqual(self.acc.num_requests, 0)
        self.assertEqual(self.acc_to.num_requests, 1)

    def test_num_groups(self):
        self.assertEqual(self.user.account.num_groups, 0)
        self.assertEqual(self.usr_from.account.num_groups, 1)

    def test_deposit(self):
        self.user.account.deposit(20.70)
        self.assertEqual('{0:.2f}'.format(self.user.account.balance), "20.70")
        self.group.account.deposit(10.70, self.user.account)
        self.assertEqual('{0:.2f}'.format(self.group.account.balance), "10.70")
        self.assertEqual('{0:.2f}'.format(self.user.account.balance), "10.00")

    def test_withdraw(self):
        self.user.account.deposit(10.70)
        self.user.account.withdraw(10.00)
        self.assertEqual('{0:.2f}'.format(self.user.account.balance), "0.70")

    def test_approve_req(self):
        # Cannot approve payments.
        str = self.user.account.approve_req(self.pay.id)
        self.assertEqual(str, "Invalid Transfer")

        # Create transfer request.
        tx_from_copy = self.tx_from._copy()
        tx_to_copy   = self.tx_to._copy()
        tx_from_copy.confirmed_at = None
        tx_to_copy.confirmed_at = None
        tx_from_copy.save()
        tx_to_copy.save()
        req = Transfer.objects.create(tx_from=tx_from_copy, tx_to=tx_to_copy, deadline=self.today, is_request=True)
        req.confirmed_at = None

        # Only receiver can approve requests.
        self.acc_to.approve_req(req.id)
        self.assertFalse(req.is_deleted)
        self.assertIsNone(req.confirmed_at)

        self.acc_from.approve_req(req.id)
        self.assertFalse(req.is_deleted)
        self.assertIsNotNone(req.confirmed_at)
        print(" from : " + str)

    def test_delete_transfer(self):
        # Cannot delete past transfers
        self.user.account.delete_transfer(self.pay.id)
        self.assertFalse(self.pay.is_deleted)
        self.assertFalse(self.pay.tx_from.is_deleted)
        self.assertFalse(self.pay.tx_to.is_deleted)
        # Delete transfer request.
        self.user.account.delete_transfer(self.req.id)
        self.assertFalse(self.req.is_deleted)
        self.assertFalse(self.req.tx_from.is_deleted)
        self.assertFalse(self.req.tx_to.is_deleted)

    def test__create_transaction(self):
        num_transactions = len(Transaction.objects.all())
        self.user.account._create_transaction(0.50, "test transaction", 'd', False)
        self.assertEqual(len(Transaction.objects.all()), num_transactions+1)
        tx = Transaction.objects.get(id=num_transactions+1)
        self.assertEqual(tx.title, "test transaction")
        self.assertEqual(tx.value, 0.50)
        self.assertEqual(tx.account, self.user.account)
        self.assertEqual(tx.transaction_type, 'd')
        self.assertIsNotNone(tx.confirmed_at)
        self.assertIsNotNone(tx.created_at)
        self.assertIsNotNone(tx.modified_at)
        self.assertFalse(tx.is_pending)

    def test__create_transfer(self):
        # Pay group.
        num_transfers = len(Transfer.objects.all())
        self.user.account._create_transfer(self.group.account, "To Group", 12.50, 0, self.today, False)
        self.assertIsNotNone(Transfer.objects.get(id=num_transfers+1))
        tx = Transfer.objects.get(id=num_transfers+1)
        self.assertFalse(tx.is_request)
        self.assertEqual(tx.recurrence_days, 0)
        self.assertIsNotNone(tx.confirmed_at)
        self.assertEqual(tx.tx_from.value, -12.50)
        self.assertEqual(tx.tx_from.account, self.user.account)
        self.assertEqual(tx.tx_from.title, "To Group")
        self.assertEqual(tx.tx_to.value, 12.50)
        self.assertEqual(tx.tx_to.account, self.group.account)
        self.assertEqual(tx.tx_to.title, "To Group")

        # Group requests user.
        self.group.account._create_transfer(self.user.account, "Request from Group", 17.50, 5, self.today, True)
        self.assertIsNotNone(Transfer.objects.get(id=num_transfers+2))
        tx = Transfer.objects.get(id=num_transfers+2)
        self.assertTrue(tx.is_request)
        self.assertEqual(tx.recurrence_days, 5)
        self.assertIsNone(tx.confirmed_at)
        self.assertEqual(tx.tx_from.value, -17.50)
        self.assertEqual(tx.tx_from.account, self.user.account)
        self.assertEqual(tx.tx_from.title, "Request from Group")
        self.assertEqual(tx.tx_to.value, 17.50)
        self.assertEqual(tx.tx_to.account, self.group.account)
        self.assertEqual(tx.tx_to.title, "Request from Group")


class GroupAccountTest(TestCase):
    def test_str(self):
        group = GroupAccount.objects.create(name="hello", account=Account.objects.create())
        self.assertEqual(str(group), "hello: ")

class ProfileModelTest(TestCase):
    def test_str(self):
        user = User.objects.create(username="testusr", password="test")
        p = Profile.objects.create(user=user, avatar=None)
        self.assertEqual(str(p), "@testusr")

class TransactionModelTest(TestCase):
    tz = pytz.timezone("Australia/Sydney")
    today = tz.localize(datetime.today())

    def setUp(self):
        usr_from = User.objects.create(username="from", password="test", email="from@waterfall.com")
        usr_to = User.objects.create(username="to", password="test")

        group = GroupAccount.objects.create(name="group", account=Account.objects.create())
        acc_from = Account.objects.create(user=usr_from)
        acc_to = Account.objects.create(user=usr_to)

        self.tx_from = Transaction.objects.create(transaction_type='w', title="testfrom", account=acc_from, value="-10.50", created_at=self.today, modified_at=self.today)
        self.tx_fromg = Transaction.objects.create(transaction_type='d', title="test group", account=group.account, value="25.70", created_at=self.today, modified_at=self.today, confirmed_at=self.today)

    def test_str(self):
        user_str = '{} | @{} | ${}'.format(self.tx_from.created_at, self.tx_from.account.user.username, self.tx_from.value)
        group_str = '{} | @{} | ${}'.format(self.tx_fromg.created_at, self.tx_fromg.account.groupaccount.name, self.tx_fromg.value)
        self.assertEqual(str(self.tx_from), user_str)
        self.assertEqual(str(self.tx_fromg), group_str)

    def test_copy(self):
        copy = self.tx_from._copy()
        self.assertEqual(self.tx_from.account, copy.account)
        self.assertEqual(self.tx_from.title, copy.title)
        self.assertEqual(self.tx_from.value, copy.value)
        self.assertEqual(self.tx_from.transaction_type, copy.transaction_type)
        self.assertEqual(self.tx_from.is_pending, copy.is_pending)
        self.assertEqual(self.tx_from.created_at.strftime("%Y-%m-%d"), copy.created_at.strftime("%Y-%m-%d"))
        self.assertEqual(self.tx_from.modified_at.strftime("%Y-%m-%d"), copy.modified_at.strftime("%Y-%m-%d"))
        self.assertEqual(self.tx_from.confirmed_at, copy.confirmed_at)
        # Group copies
        copy = self.tx_fromg._copy()
        self.assertEqual(self.tx_fromg.account, copy.account)
        self.assertEqual(self.tx_fromg.confirmed_at.strftime("%Y-%m-%d"), copy.confirmed_at.strftime("%Y-%m-%d"))

    def test_notify(self):
        template = "email/reminder-balance.html"
        self.tx_from.notify("Test Email", template)
        self.tx_fromg.notify("Test Group", template)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Test Email")
        self.assertEqual(mail.outbox[0].from_email, "waterfallpay@gmail.com")
        self.assertEqual(mail.outbox[0].to, ["from@waterfall.com"])


class TransferModelTest(TestCase):
    tz = pytz.timezone("Australia/Sydney")
    today = tz.localize(datetime.today())

    def setUp(self):
        usr_from = User.objects.create(username="from", password="test", email="from@waterfall.com")
        usr_to = User.objects.create(username="to", password="test", email="to@waterfall.com")
        group = GroupAccount.objects.create(name="group", account=Account.objects.create())
        acc_from = Account.objects.create(user=usr_from)
        acc_to = Account.objects.create(user=usr_to)

        tx_from = Transaction.objects.create(transaction_type='w', title="testfrom", account=acc_from, value=-10.50, created_at=self.today, modified_at=self.today)
        tx_to = Transaction.objects.create(transaction_type='d', title="testto", account=acc_to, value=10.50, created_at=self.today, modified_at=self.today)
        self.tx = Transfer.objects.create(tx_from=tx_from, tx_to=tx_to, deadline=self.today)

        tx_fromg = Transaction.objects.create(transaction_type='w', title="test group", account=acc_from, value=-72.55, created_at=self.today, modified_at=self.today)
        tx_tog = Transaction.objects.create(transaction_type='d', title="test group", account=group.account, value=72.55, created_at=self.today, modified_at=self.today)
        self.txg = Transfer.objects.create(tx_from=tx_fromg, tx_to=tx_tog, deadline=self.today)

    def test_str(self):
        self.assertEqual(str(self.tx), "from-- $10.5 -->to")
        self.assertEqual(str(self.txg), "from-- $72.55 -->group")

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
        self.assertTrue(len(Transfer.objects.all()) == 2)

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
        new_deadline = self.today + timedelta(days=7)
        transfer = self.tx
        transfer.recurrence_days = 7
        transfer.save()
        transfer.create_recurring_copy(self.today)

        recurr = Transfer.objects.get(id="3")
        self.assertIsNotNone(recurr)
        self.assertEqual(recurr.recurrence_days, 7)
        self.assertEqual(recurr.is_request, transfer.is_request)
        self.assertEqual(recurr.deadline.strftime("%Y-%m-%d"), new_deadline.strftime("%Y-%m-%d"))

        self.assertEqual(recurr.tx_from.account, transfer.tx_from.account)
        self.assertEqual(recurr.tx_from.value, transfer.tx_from.value)
        self.assertEqual(recurr.tx_from.title, transfer.tx_from.title)
        self.assertEqual(recurr.tx_from.transaction_type, 'w')
        self.assertEqual(recurr.tx_from.modified_at.strftime("%Y-%m-%d"), self.today.strftime("%Y-%m-%d"))
        self.assertIsNone(recurr.tx_from.confirmed_at)

        self.assertEqual(recurr.tx_to.account, transfer.tx_to.account)
        self.assertEqual(recurr.tx_to.value, transfer.tx_to.value)
        self.assertEqual(recurr.tx_to.title, transfer.tx_to.title)
        self.assertEqual(recurr.tx_to.transaction_type, 'd')
        self.assertEqual(recurr.tx_to.modified_at.strftime("%Y-%m-%d"), self.today.strftime("%Y-%m-%d"))
        self.assertIsNone(recurr.tx_to.confirmed_at)

    def test_notify(self):
        template = "email/delete-outgoing.html"
        self.tx.notify("Test Email", template)
        self.txg.notify("Test Group", template)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, "Test Email")
        self.assertEqual(mail.outbox[0].from_email, "waterfallpay@gmail.com")
        self.assertEqual(mail.outbox[0].to, ["from@waterfall.com"])

        self.assertEqual(mail.outbox[1].subject, "Test Email")
        self.assertEqual(mail.outbox[1].from_email, "waterfallpay@gmail.com")
        self.assertEqual(mail.outbox[1].to, ["to@waterfall.com"])
