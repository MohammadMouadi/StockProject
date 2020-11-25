from django.contrib.auth.models import User
from django.test import TestCase
import datetime
from myapp import models
from myapp.logic import trade_logic


class TestTradeLogic(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_get_stock_price(self):
        stock_price = trade_logic.get_stock_price('A')
        self.assertIsNotNone(stock_price)

    def test_create_transaction(self):
        stock_info = {
            'stock_symbol': 'A',
            'number_of_stocks': 10,
            'price': 3.0
        }

        trade_logic.create_transaction(user=self.user, **stock_info)

        does_exist = models.Transaction.objects.filter(user=self.user).exists()
        self.assertTrue(does_exist)

    def test_get_number_of_stocks(self):
        stock_info = {
            'stock_symbol': 'A',
            'number_of_stocks': 10,
            'price': 3.0
        }
        trade_logic.create_transaction(user=self.user, **stock_info)

        stock_info = {
            'stock_symbol': 'A',
            'number_of_stocks': -5,
            'price': 3.0
        }
        trade_logic.create_transaction(user=self.user, **stock_info)

        number_of_stocks = trade_logic.get_number_of_stocks(self.user, 'A')
        self.assertEqual(number_of_stocks, 5)

class TestLargeNumberOfTransactions(TestCase):
    def setUp(self):
        self.mock_stock_list = [{'stock_symbol': 'A',
                            'number_of_stocks': 10,
                            'price': 100},
                           {'stock_symbol': 'B',
                            'number_of_stocks': 5,
                            'price': 40},
                           ]

        self.NUMBER_OF_USERS = 20
        self.NUMBER_OF_TRANSACTIONS = 10000
        for i in range(self.NUMBER_OF_USERS):
            user = User.objects.create_user(username=f'testuser{i}', password=f"123456{i}")
            index = i // (self.NUMBER_OF_USERS // 2)  # index = 0 for first half of iterations and 1 for the next half of iterations
            for j in range(self.NUMBER_OF_TRANSACTIONS):
                trade_logic.create_transaction(user, **self.mock_stock_list[index])


    def test_large_number_of_transactions(self):
        start_time = datetime.datetime.now()
        random_user = User.objects.get_by_natural_key('testuser0')
        number_of_stocks = trade_logic.get_number_of_stocks(random_user, self.mock_stock_list[0]['stock_symbol'])
        expected_number_of_stocks = self.NUMBER_OF_TRANSACTIONS * self.mock_stock_list[0]['number_of_stocks']
        self.assertEqual(expected_number_of_stocks, number_of_stocks)
        end_time=datetime.datetime.now()
        self.assertLess((end_time-start_time).total_seconds(),1)

