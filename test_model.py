import pytest

import model as m
from Transaction import Transaction
import unittest
import sqlite3
from unittest.mock import patch, MagicMock, Mock


def test_calculate_transaction_cost():
    assert m.calculate_transaction_cost(1, 50, 7) == 57


def test_calculate_transaction_revenue():
    assert m.calculate_transaction_revenue(1, 50, 7) == 43


def test_mytest():
    with pytest.raises(SystemExit):
        m.f()


def test_lookup_ticker_symbol_success():
    assert m.lookup_ticker_symbol('Apple') == 'AAPL'


def test_lookup_ticker_symbol_fail():
    assert Exception()


def test_transaction_class():
    t1 = Transaction(
        last_price=124.5,
        brokerage_fee=10.50,
        current_balance=100000,
        trade_volume=5.0,
        new_balance=m.calculate_transaction_cost(5, 124.5, 10.50),
        ticker_symbol='AAPL',
        current_number_shares=500.0
    )

    t2 = Transaction(
        last_price=124.5,
        brokerage_fee=10.50,
        current_balance=100000,
        trade_volume=5.0,
        new_balance=m.calculate_transaction_cost(5, 124.5, 10.50),
        ticker_symbol='AAPL',
        current_number_shares=500.0
    )

    assert t1 == t2


def test_current_user():
    with patch('model.sqlite3') as mock_sql:
        mock_sql.connect().cursor().fetchone.return_value = ['paulina']

        assert m.current_user() == 'paulina'

class TestLogIn:
    def test_log_in_success(self):
        with patch('model.sqlite3') as mock_sql:
            mock_sql.connect().cursor().fetchone.return_value = ('307e1fb4b8594b49b8eb119a4a38cc5020fd9eb18afa9a38b8c75abb4ac8ae6e','86f712b2c0e419af5f9cfc53f0bd9f0b3cb0c81e4d9299125f2e9e99e504f3a7f2b534894ffbdca10ce0a5507142c91a4d66f859f6df5771ba04e5fa477f28e0')
            assert m.log_in('asdf', 'asdf') == True
            mock_sql.connect().cursor().fetchone.return_value = ['asdf']
            assert m.current_user() == 'asdf'

    def test_log_in_failure(self):
        with patch('model.sqlite3') as mock_sql:
            mock_sql.connect().cursor().fetchone.return_value = ('asdf','asdf')
            assert m.log_in('asdf', 'asdf') == False

class TestCreate:
    def test_create_success(self):
        with patch('model.sqlite3') as mock_sql:
            assert m.create_('asdf', 'asdf', 124532523525) == True

    def test_create_fail_no_username(self):
        with patch('model.sqlite3') as mock_sql:
            assert m.create_('', 'asdf', 124532523525) == False

    def test_create_fail_no_password(self):
        with patch('model.sqlite3') as mock_sql:
            assert m.create_('asdf', '', 124532523525) == False

    def test_create_fail_negative_value(self):
        with patch('model.sqlite3') as mock_sql:
            assert m.create_('asdf', 'asdf', -124532523525) == False

def test_update_holdings():
    with patch('model.sqlite3') as mock_sql:
        m.update_holdings()
