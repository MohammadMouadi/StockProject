from django.test import TestCase
from myapp.models import Stock, UserProfile, Transaction
from django.utils import timezone
from django.contrib.auth.models import User

#django.utils.timezone.now

class BaseTest(TestCase):
    SYMBOL_LENGTH = 12
    NAME_LENGTH = 64
    PRIMARY_EXCHANGE_LENGTH = 32

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Stock.objects.create(symbol='1', name='test_stock', price=3.5, change_percent=5, )
        user = User.objects.create_user('Alaa', 'Yahia', 'alaa.yahia.1995@gmail.com')
        UserProfile.objects.create(user=user, balance=500)
        Transaction.objects.create(user=user,
                                   stock_symbol=Stock.objects.get(symbol='1').symbol,
                                   trans_date_time=timezone.now(),
                                   quantity=3,
                                   price=Stock.objects.get(symbol='1').price)


class TransactionModelTest(BaseTest):

    def test_transaction_not_None(self):
        self.assertEquals(1,2)
        transaction = Transaction.objects.get()
        self.assertIsNotNone(transaction.user_id)

    def test_user_id(self):
        transaction = Transaction.objects.get()
        self.assertEquals('Alaa', transaction.user.username)

    def test_stock_symbol(self):
        transaction = Transaction.objects.get()
        self.assertEquals('1', transaction.stock_symbol)

    def test_trans_date_time(self):
        transaction = Transaction.objects.get()
        self.assertIsNotNone(transaction.trans_date_time)

    def test_quantity(self):
        transaction = Transaction.objects.get()
        self.assertEquals(3, transaction.quantity)

    def test_price(self):
        transaction = Transaction.objects.get()
        self.assertEquals(3.5, transaction.price)


class UserProfileModelTest(BaseTest):

    def test_user_not_None(self):
        user_profile = UserProfile.objects.get()
        self.assertIsNotNone(user_profile.user)

    def test_user_username(self):
        user_profile = UserProfile.objects.get()
        self.assertEquals('Alaa', user_profile.user.username)

    def test_user_balance(self):
        user_profile = UserProfile.objects.get()
        self.assertEquals(500, user_profile.balance)


class StockModelTest(BaseTest):

    def test_symbol_length(self):
        stock = Stock.objects.get(symbol='1')
        max_length = stock._meta.get_field('symbol').max_length
        self.assertEquals(max_length, self.SYMBOL_LENGTH)

    def test_symbol_not_none(self):
        stock = Stock.objects.get(symbol='1')
        self.assertIsNotNone(stock.symbol)

    def test_name_length(self):
        stock = Stock.objects.get(symbol='1')
        max_length = stock._meta.get_field('name').max_length
        self.assertEquals(max_length, self.NAME_LENGTH)

    def test_name_not_none(self):
        stock = Stock.objects.get(symbol='1')
        self.assertIsNotNone(stock.name)

    def test_price_not_none(self):
        stock = Stock.objects.get(symbol='1')
        self.assertIsNotNone(stock.price)

    def test_change_percent_not_none(self):
        stock = Stock.objects.get(symbol='1')
        self.assertIsNotNone(stock.change_percent)

    def test_primary_excahnge_length(self):
        stock = Stock.objects.get(symbol='1')
        max_length = stock._meta.get_field('primary_exchange').max_length
        self.assertEquals(max_length, self.PRIMARY_EXCHANGE_LENGTH)
