from django.test import TestCase
from django.contrib.auth import authenticate
from .models import User, Profile, Account, Transfer, Transaction
from datetime import datetime, timedelta, tzinfo
import pytz

class ProfileModelTest(TestCase):
    name = "test-user"
    pw = "test"

    def test_str(self):
        user = User.objects.create(username=self.name, password=self.pw)
        p = Profile.objects.create(user=user, avatar=None)
        self.assertEqual(str(p), "@"+self.name)

class TransferModelTest(TestCase):
    def setUp(self):
        usr_from = User.objects.create(username="from", password="test")
        usr_to = User.objects.create(username="to", password="test")
        acc_from = Account.objects.create(user=usr_from)
        acc_to = Account.objects.create(user=usr_to)
        tx_from = Transaction.objects.create(transaction_type='w', title="testfrom", account=acc_from, value="-10.50")
        tx_to = Transaction.objects.create(transaction_type='d', title="testto", account=acc_to, value="10.50")
        Transfer.objects.create(tx_from=tx_from, tx_to=tx_to)

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
        today = datetime.today()
        transfer = Transfer.objects.get(id="1")
        transfer.confirm(today)
        self.assertEqual(transfer.confirmed_at, today)
        self.assertEqual(transfer.tx_from.confirmed_at, today)
        self.assertEqual(transfer.tx_to.confirmed_at, today)
        self.assertFalse(transfer.tx_from.is_pending)
        self.assertFalse(transfer.tx_to.is_pending)
        # Check that no copy has been made.
        self.assertTrue(len(Transfer.objects.all()) < 2)

    def test_confirm_recurr(self):
        today = datetime.today()
        transfer = Transfer.objects.get(id="1")
        transfer.recurrence_days = 7
        transfer.save()
        transfer.confirm(today)
        self.assertEqual(transfer.confirmed_at, today)
        self.assertEqual(transfer.tx_from.confirmed_at, today)
        self.assertEqual(transfer.tx_to.confirmed_at, today)
        self.assertFalse(transfer.tx_from.is_pending)
        self.assertFalse(transfer.tx_to.is_pending)
        # Check that no copy has been made.
        self.assertIsNotNone(Transfer.objects.get(id="2"))

    def test_recurring_copy(self):
        tz = pytz.timezone("Australia/Sydney")
        today = tz.localize(datetime.now())
        new_deadline = today + timedelta(days=7)
        transfer = Transfer.objects.get(id="1")
        transfer.recurrence_days = 7
        transfer.save()
        transfer.create_recurring_copy(today)

        recurr = Transfer.objects.get(id="2")
        self.assertIsNotNone(recurr)
        # TODO steph
        utc_delta = datetime.utcnow() - datetime.now()
        utc_date = new_deadline + utc_delta
        utc_date = utc_date.replace(tzinfo=pytz.UTC)
        self.assertEqual(recurr.deadline.date(), utc_date.date())
        self.assertEqual(recurr.recurrence_days, 7)
        self.assertEqual(recurr.is_request, transfer.is_request)

        self.assertEqual(recurr.tx_from.account, transfer.tx_from.account)
        self.assertEqual(recurr.tx_from.value, transfer.tx_from.value)
        self.assertEqual(recurr.tx_from.title, transfer.tx_from.title)
        self.assertEqual(recurr.tx_from.transaction_type, 'w')
        self.assertEqual(recurr.tx_from.modified_at, today)
        self.assertIsNone(recurr.tx_from.confirmed_at)

        self.assertEqual(recurr.tx_to.account, transfer.tx_to.account)
        self.assertEqual(recurr.tx_to.value, transfer.tx_to.value)
        self.assertEqual(recurr.tx_to.title, transfer.tx_to.title)
        self.assertEqual(recurr.tx_to.transaction_type, 'd')
        self.assertEqual(recurr.tx_to.modified_at, today)
        self.assertIsNone(recurr.tx_to.confirmed_at)


    def test_notify(self):
        # TODO test email notification
        return True
