import pytest

import model as m
from Transaction import Transaction


def test_calculate_transaction_cost():
    assert m.calculate_transaction_cost(1, 50, 7) == 57


def test_calculate_transaction_revenue():
    assert m.calculate_transaction_revenue(1, 50, 7) == 43


def test_mytest():
    with pytest.raises(SystemExit):
        m.f()


# def test_lookup_ticker_symbol_success():
#     assert m.lookup_ticker_symbol('Apple') == 'AAPL'


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
