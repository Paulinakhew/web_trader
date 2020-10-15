#!/usr/bin/env python3

import binascii
import datetime
import hashlib
import json
import os
import sqlite3

import requests
from dotenv import load_dotenv

from Transaction import Transaction

load_dotenv()
api_key = os.environ.get("API_KEY")


def current_user():
    '''Selects the username of the current user from the current_user db

    Returns:
        username (str): the current user's username
    '''
    connection = sqlite3.connect('trade_information.db', check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(
        '''
            SELECT username
            FROM current_user;
        '''
    )
    username = cursor.fetchone()

    return username[0]


def log_in(user_name, password):
    '''Logs the user in if they exist in the user db

    Parameters:
        user_name: (str) a username mapped to a single user
        password: (str) a password belonging to the user

    Returns:
        (bool) a boolean that represents whether or not the user was successfully logged in
    '''
    connection = sqlite3.connect('trade_information.db', check_same_thread=False)
    cursor = connection.cursor()

    cursor.execute(
        f'''
            SELECT salt, key
            FROM user
            WHERE username = "{user_name}";
        '''
    )

    result_tuple = cursor.fetchone()

    salt = result_tuple[0]
    key = result_tuple[1]

    pwdhash = hashlib.pbkdf2_hmac(
        'sha512',
        password.encode('utf-8'),
        salt.encode('ascii'),
        100000
    )

    pwdhash = binascii.hexlify(pwdhash).decode('ascii')

    if key == pwdhash:
        cursor.execute(
            f'''
                UPDATE current_user
                SET username = "{user_name}"
                WHERE pk = 1;
            '''
        )
        connection.commit()
        cursor.close()
        connection.close()
        return True
    cursor.close()
    connection.close()
    return False


def create_(new_user, new_password, new_fund):
    '''Adds a new user into the user database if the username is unique

    Parameters:
        new_user (str): a new username
        new_password (str): new user's password that ends up being hashed
        new_fund (float): the amount of money the user starts the game with

    Returns:
        boolean representing whether or not the user was successfully created and inserted into user db
    '''
    connection = sqlite3.connect('trade_information.db', check_same_thread=False)
    cursor = connection.cursor()

    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', new_password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)

    try:
        cursor.execute(
            f'''INSERT INTO user(
                username,
                salt,
                key,
                current_balance
                ) VALUES(
                "{new_user}",
                "{salt.decode('ascii')}",
                "{pwdhash.decode('ascii')}",
                {new_fund}
            );'''
        )
        connection.commit()
        return True
    except:
        print('There was an error with creating a user.')
        return False

    cursor.close()
    connection.close()


def update_holdings():
    '''Deletes records from holdings if the number of shares are equal to zero'''
    connection = sqlite3.connect('trade_information.db', check_same_thread=False)
    cursor = connection.cursor()
    query = 'DELETE FROM holdings WHERE num_shares = 0.0'
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()


def sell(username, ticker_symbol, trade_volume):
    '''Sells the stock if the user has enough quantity of the stock

    Search for how many of the stock the user has and sells them if the trade volume is less than the stock.
    If the trade volume is greater than the stock, return to menu.

    Params:
        username: (str) username of current user from db
        ticker_symbol: (str) ticker symbol of stock that is going to be sold
        trade_volume: (float) the number of stocks the user wants to sell

    Returns:
        boolean that describes whether or not the transaction was successful
        transaction: a instance of the Transaction class
    '''
    username = current_user()
    database = 'trade_information.db'
    connection = sqlite3.connect(database, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(
        f'''
            SELECT count(*),
            num_shares
            FROM holdings
            WHERE username = "{username}"
            AND ticker_symbol = "{ticker_symbol}"
        '''
    )
    fetch_result = cursor.fetchone()

    if fetch_result[0] == 0:
        current_number_shares = 0
    else:
        current_number_shares = fetch_result[1]

    last_price = float(quote_last_price(ticker_symbol))
    brokerage_fee = 6.95  # TODO: un-hardcode this value
    current_balance = get_user_balance(username)
    transaction_revenue = calculate_transaction_revenue(trade_volume, last_price, brokerage_fee)
    agg_balance = float(current_balance) + float(transaction_revenue)

    transaction = Transaction(
        last_price=last_price,
        brokerage_fee=brokerage_fee,
        current_balance=current_balance,
        trade_volume=trade_volume,
        new_balance=agg_balance,
        ticker_symbol=ticker_symbol,
        current_number_shares=current_number_shares
    )

    if current_number_shares >= trade_volume:
        return True, transaction
    else:
        return False, transaction
    # if yes return new balance = current balance - transaction cost


def calculate_transaction_revenue(trade_volume, last_price, brokerage_fee):
    '''Calculates transaction revenue

    Parameters:
        trade_volume (float): the amount of stocks that the user wants to sell
        last_price (float): the last price of the stock
        brokerage_fee (float): price of the transaction

    Returns:
        transaction_revenue (float): the amount that that user earns from the transaction
    '''
    transaction_revenue = (trade_volume * last_price) - brokerage_fee

    return transaction_revenue


def sell_db(transaction):
    '''Updates the user's holdings and transactions once the user decides to sell the stock

    Params:
        transaction (Transaction class instance): contains all of the information related to the transaction
    '''
    database = 'trade_information.db'
    connection = sqlite3.connect(database, check_same_thread=False)
    cursor = connection.cursor()

    last_price = transaction.last_price
    trade_volume = transaction.trade_volume
    agg_balance = transaction.current_balance
    username = current_user()
    ticker_symbol = transaction.ticker_symbol
    current_number_shares = transaction.current_number_shares

    now = datetime.datetime.now()
    date = now.strftime('%Y-%m-%d %I:%M %p')

    # update the user table with updated balance after selling
    cursor.execute(
        f'''
            UPDATE user
            SET current_balance = {agg_balance}
            WHERE username = "{username}";
        '''
    )

    # update the transactions table
    cursor.execute(
        f'''
            INSERT INTO transactions(
                ticker_symbol,
                num_shares,
                owner_username,
                last_price,
                date
            ) VALUES(
                "{ticker_symbol}",
                {trade_volume*-1},
                "{username}",
                {last_price},
                "{date}"
            );
        '''
    )

    # update the holdings table
    if current_number_shares >= trade_volume:
        tot_shares = float(current_number_shares) - float(trade_volume)
        cursor.execute(
            f'''
                UPDATE holdings
                SET num_shares = {tot_shares}, last_price = {last_price}
                WHERE username = "{username}"
                AND ticker_symbol = "{ticker_symbol}";
            '''
        )

    connection.commit()
    cursor.close()
    connection.close()


def buy(username, ticker_symbol, trade_volume):
    '''Returns whether or not the user can buy the selected quantity of the stock

    Parameters:
        username (str): the name of the current user
        ticker_synbol (str): submitted ticker symbol
        trade_volume (float): the amount of the stock the user wants to sell

    Returns:
        boolean representing whether or not the user can buy the stock
    '''
    trade_volume = float(trade_volume)
    last_price = float(quote_last_price(ticker_symbol))
    brokerage_fee = 6.95  # TODO: un-hardcode this value
    username = current_user()
    current_balance = get_user_balance(username)
    transaction_cost = calculate_transaction_cost(trade_volume, last_price, brokerage_fee)
    left_over = float(current_balance) - float(transaction_cost)

    transaction = Transaction(
        last_price=last_price,
        brokerage_fee=brokerage_fee,
        current_balance=current_balance,
        trade_volume=trade_volume,
        new_balance=left_over,
        ticker_symbol=ticker_symbol,
        current_number_shares=None
    )
    if transaction_cost <= current_balance:
        return True, transaction
    else:
        return False, transaction
    # if yes return new balance = current balance - transaction cost


def calculate_transaction_cost(trade_volume, last_price, brokerage_fee):
    transaction_cost = (trade_volume * last_price) + brokerage_fee

    return transaction_cost


def buy_db(transaction):
    connection = sqlite3.connect('trade_information.db', check_same_thread=False)
    cursor = connection.cursor()
    database = 'trade_information.db'
    username = current_user()
    connection = sqlite3.connect(database, check_same_thread=False)
    cursor = connection.cursor()

    last_price = transaction.last_price
    trade_volume = transaction.trade_volume
    left_over = transaction.new_balance
    username = current_user()
    ticker_symbol = transaction.ticker_symbol
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d %I:%M %p")

    # users
    cursor.execute(
        f'''
            UPDATE user
            SET current_balance = {left_over}
            WHERE username = "{username}";
        '''
    )

    # transactions
    cursor.execute(
        f'''INSERT INTO transactions(
            ticker_symbol,
            num_shares,
            owner_username,
            last_price,
            date
        ) VALUES(
            "{ticker_symbol}",
            {trade_volume},
            "{username}",
            {last_price},
            "{date}"
        );'''
    )

    # holdings
    cursor.execute(
        f"""
            SELECT count(*), num_shares
            FROM holdings
            WHERE username = '{username}'
            AND ticker_symbol = '{ticker_symbol}'
        """
    )
    fetch_result = cursor.fetchone()
    if fetch_result[0] == 0:  # if the user didn't own the specific stock
        cursor.execute(
            f'''INSERT INTO holdings(
                last_price,
                num_shares,
                ticker_symbol,
                username
            ) VALUES (
                {last_price},
                {trade_volume},
                "{ticker_symbol}",
                "{username}"
            );'''
        )
    else:  # if the user already has the same stock
        tot_shares = float(fetch_result[1])+float(trade_volume)
        cursor.execute(
            f'''
                UPDATE holdings
                SET num_shares = {tot_shares}, last_price = {last_price}
                WHERE username = "{username}"
                AND ticker_symbol = "{ticker_symbol}";
            '''
        )
    connection.commit()
    cursor.close()
    connection.close()


def get_user_balance(username):
    username = current_user()
    connection = sqlite3.connect('trade_information.db', check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(
        f"""
            SELECT current_balance
            FROM user
            WHERE username = '{username}';
        """
    )
    fetched_result = cursor.fetchone()
    cursor.close()
    connection.close()

    return fetched_result[0]


def lookup_ticker_symbol(company_name):
    try:
        endpoint = f"https://api-v2.intrinio.com/companies/search?query={company_name}&api_key={api_key}"

        ticker_symbol = json.loads(requests.get(endpoint).text)['companies'][0]['ticker']
        assert ticker_symbol
        return ticker_symbol
    except IndexError:
        raise Exception('There was no company found.')


def quote_last_price(ticker_symbol):
    try:
        endpoint = f"https://api-v2.intrinio.com/securities/{ticker_symbol}/prices/realtime?api_key={api_key}"
        last_price = json.loads(requests.get(endpoint).text)['last_price']
        assert last_price
        return last_price

    except IndexError:
        raise Exception('There was no last price found.')


def display_user_holdings():
    username = current_user()
    connection = sqlite3.connect("trade_information.db", check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(f"SELECT ticker_symbol,num_shares,last_price FROM holdings WHERE username='{username}';")
    user_holdings = cursor.fetchall()
    cursor.close()
    connection.close()
    return user_holdings


def display_user_transactions():
    username = current_user()
    connection = sqlite3.connect("trade_information.db", check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(
        f"""
            SELECT ticker_symbol,
            num_shares,
            last_price,
            date
            FROM transactions
            WHERE owner_username='{username}';
        """
    )
    user_transactions = cursor.fetchall()
    cursor.close()
    connection.close()
    return user_transactions


def get_users_with_holdings():
    connection = sqlite3.connect("trade_information.db", check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(
        """
            SELECT username
            FROM holdings
            WHERE username NOT LIKE 'admin';
        """
    )
    users = list(cursor.fetchall())  # List of tuples
    users_list = [str(user) for user in users]  # List of strings
    cursor.close()
    connection.close()
    return users_list


def get_tkr_symb_from_holdings():
    connection = sqlite3.connect("trade_information.db", check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(
        """
            SELECT ticker_symbol
            FROM holdings
            WHERE username NOT LIKE 'admin';
        """
    )
    symbols = cursor.fetchall()
    symbols_list = [str(sym[0]) for sym in symbols]
    cursor.close()
    connection.close()
    return symbols_list


def update_leaderboard():
    connection = sqlite3.connect('trade_information.db', check_same_thread=False)
    cursor = connection.cursor()
    username = get_users_with_holdings()
    for user in username:
        ticker_symbol = cursor.execute(
            f"""
                SELECT ticker_symbol
                FROM holdings
                WHERE username='{user}';
            """
        )
        mkt_val = cursor.execute(
            f"""
                SELECT (num_shares*last_price)
                FROM transactions
                WHERE owner_username = '{user}'
                AND ticker_symbol = '{ticker_symbol}';
            """
        )

        cursor.execute(
            f"""
                UPDATE leaderboard
                SET p_and_l={mkt_val}
                WHERE username='{username}';
            """
        )
    connection.commit()
    cursor.close()
    connection.close()


def log_out():
    connection = sqlite3.connect('trade_information.db', check_same_thread=False)
    cursor = connection.cursor()

    cursor.execute(
        """
            REPLACE INTO current_user(
                pk,
                username
            ) VALUES (
                1,
                'randomuser'
            );
        """
    )
    connection.commit()
    cursor.close()
    connection.close()


def f():
    raise SystemExit(1)
