from django.test import TestCase
from django.contrib.auth import authenticate
from .models import User, Profile, Account, Transfer, Transaction
from datetime import datetime
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

    def test_confirm_norecurr(self):
        today = datetime.today()
        transfer = Transfer.objects.get(id="1")
        transfer.confirm(today)
        self.assertEqual(transfer.confirmed_at, today)
        self.assertEqual(transfer.tx_from.confirmed_at, today)
        self.assertEqual(transfer.tx_to.confirmed_at, today)
        self.assertFalse(transfer.tx_from.is_pending)
        self.assertFalse(transfer.tx_to.is_pending)
        # Check that no copy has been made.
        self.assertIsNone(Transfer.objects.get(id="2"))

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
        self.assertIsNotNone(obj, msg)Transfer.objects.get(id="2"))
