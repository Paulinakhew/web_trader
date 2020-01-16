#!/usr/bin/env

import os
from dotenv import load_dotenv
import json
import sqlite3
import requests
import datetime

from Transaction import Transaction

project_folder = os.path.expanduser('.')
load_dotenv(os.path.join(project_folder, '.env'))

api_key = os.getenv("API_KEY")


def current_user():
    '''Selects the username of the current user from the current_user db'''
    connection = sqlite3.connect('trade_information.db', check_same_thread=False)
    cursor = connection.cursor()
    query = 'SELECT username FROM current_user;'
    cursor.execute(query)
    username = cursor.fetchone()

    return username[0]


def log_in(user_name, password):
    '''Logs the user in if they exist in the user db

    Parameters:
        user_name: (str) a username mapped to a single user
        password: (str) a password belonging to the user

    Returns:
        (bool) a boolean that represents whether or not the user exists in the user db
    '''
    connection = sqlite3.connect('trade_information.db', check_same_thread=False)
    cursor = connection.cursor()
    query = f"SELECT count(*) FROM user WHERE username = '{user_name}' AND password = '{password}';"
    cursor.execute(query)
    result_tuple = cursor.fetchone()

    if result_tuple[0] == 0:
        return False
    elif result_tuple[0] == 1:
        cursor.execute(f"UPDATE current_user SET username = '{user_name}' WHERE pk = 1;")
        connection.commit()
        return True
    else:
        pass

    cursor.close()
    connection.close()


def create_(new_user, new_password, new_fund):
    connection = sqlite3.connect('trade_information.db', check_same_thread=False)
    cursor = connection.cursor()

    try:
        cursor.execute(
            f"""INSERT INTO user(
                username,
                password,
                current_balance
                ) VALUES(
                "{new_user}",
                "{new_password}",
                {new_fund}
            );"""
        )
        connection.commit()
        return True
    except AssertionError as error:
        print(error)
        print('There was an error with creating a user.')
        return False

    cursor.close()
    connection.close()


def update_holdings():
    connection = sqlite3.connect('trade_information.db', check_same_thread=False)
    cursor = connection.cursor()
    query = 'DELETE FROM holdings WHERE num_shares = 0.0'
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()


def sell(username, ticker_symbol, trade_volume):
    '''Sells the stock if the user has enough

    Search for how many of the stock the user has and sells them if the trade volume is less than the stock.
    If the trade volume is greater than the stock, return to menu.

    Params:
        username: (str) username of current user from db
        ticker_symbol: (str) ticker symbol of stock that is going to be sold
        trade_volume: (float) the number of stocks the user wants to sell
    '''
    username = current_user()
    database = 'trade_information.db'
    connection = sqlite3.connect(database, check_same_thread=False)
    cursor = connection.cursor()
    query = f"SELECT count(*), num_shares FROM holdings WHERE username = '{username}' AND ticker_symbol = '{ticker_symbol}'"
    cursor.execute(query)
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
    return_list = (
        last_price,
        brokerage_fee,
        current_balance,
        trade_volume,
        agg_balance,
        username,
        ticker_symbol,
        current_number_shares
    )

    if current_number_shares >= trade_volume:
        return True, return_list  # success
    else:
        return False, return_list
    # if yes return new balance = current balance - transaction cost


def calculate_transaction_revenue(trade_volume, last_price, brokerage_fee):
    transaction_revenue = (trade_volume * last_price) - brokerage_fee

    return transaction_revenue


def sell_db(return_list):
    # check if user holds enough stock
    # update user's balance
    # insert transaction
    # if user sold all stocks holdings row should be deleted not set to 0
    database = 'trade_information.db'
    connection = sqlite3.connect(database, check_same_thread=False)
    cursor = connection.cursor()
    last_price = return_list[0]
    # brokerage_fee = return_list[1]
    # current_balance = return_list[2]
    trade_volume = return_list[3]
    agg_balance = return_list[4]
    username = current_user()
    ticker_symbol = return_list[6]
    current_number_shares = return_list[7]

    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d %I:%M %p")

    # user
    cursor.execute(
        f"""UPDATE user
        SET current_balance = {agg_balance}
        WHERE username = '{username}';"""
    )

    # transactions
    cursor.execute(
        f"""INSERT INTO transactions(
        ticker_symbol,
        num_shares,
        owner_username,
        last_price,
        date
        ) VALUES(
        '{ticker_symbol}',{trade_volume*-1},'{username}',{last_price}, '{date}'
        );"""
    )

    # holdings
    # at this point, it it assumed that the user has enough shares to sell.
    if current_number_shares >= trade_volume:  # if user isn't selling all shares of a specific company
        tot_shares = float(current_number_shares)-float(trade_volume)
        cursor.execute(
            f'''UPDATE holdings
            SET num_shares = {tot_shares}, last_price = {last_price}
            WHERE username = "{username}" AND ticker_symbol = "{ticker_symbol}";'''
        )

    connection.commit()
    cursor.close()
    connection.close()


def buy(username, ticker_symbol, trade_volume):
    # we need to return True or False for the confirmation message
    trade_volume = float(trade_volume)
    last_price = float(quote_last_price(ticker_symbol))
    brokerage_fee = 6.95  # TODO: un-hardcode this value
    username = current_user()
    current_balance = get_user_balance(username)
    transaction_cost = calculate_transaction_cost(trade_volume, last_price, brokerage_fee)
    left_over = float(current_balance) - float(transaction_cost)
    transaction = Transaction(username, last_price, brokerage_fee, current_balance, trade_volume, left_over, ticker_symbol)
    print(transaction)
    return_list = (last_price, brokerage_fee, current_balance, trade_volume, left_over, username, ticker_symbol)
    if transaction_cost <= current_balance:
        return True, return_list  # success
    else:
        return False, return_list
    # if yes return new balance = current balance - transaction cost


def calculate_transaction_cost(trade_volume, last_price, brokerage_fee):
    transaction_cost = (trade_volume * last_price) + brokerage_fee

    return transaction_cost


def buy_db(return_list):
    # return_list = (last_price, brokerage_fee, current_balance, trade_volume, left_over, username, ticker_symbol)
    connection = sqlite3.connect('trade_information.db', check_same_thread=False)
    cursor = connection.cursor()
    database = 'trade_information.db'
    username = current_user()
    connection = sqlite3.connect(database, check_same_thread=False)
    cursor = connection.cursor()
    last_price = return_list[0]
    # brokerage_fee = return_list[1]
    # current_balance = return_list[2]
    trade_volume = return_list[3]
    left_over = return_list[4]
    username = return_list[5]
    ticker_symbol = return_list[6]
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d %I:%M %p")

    # update users(current_balance), stocks, holdings.
    # users
    # updating the balance of the user
    cursor.execute(
        f"""UPDATE user
        SET current_balance = {left_over}
        WHERE username = '{username}';"""
    )
    # transactions
    cursor.execute(
        f"""INSERT INTO transactions(
            ticker_symbol,
            num_shares,
            owner_username,
            last_price,
            date
        ) VALUES(
            '{ticker_symbol}',{trade_volume},'{username}',{last_price},'{date}'
        );"""
    )

    # inserting information
    # holdings
    query = f'SELECT count(*), num_shares FROM holdings WHERE username = "{username}" AND ticker_symbol = "{ticker_symbol}"'
    cursor.execute(query)
    fetch_result = cursor.fetchone()
    if fetch_result[0] == 0:  # if the user didn't own the specific stock
        cursor.execute(
            f'''INSERT INTO holdings(
                last_price,
                num_shares,
                ticker_symbol,
                username
            ) VALUES (
                {last_price},{trade_volume},"{ticker_symbol}","{username}"
            );'''
        )
    else:  # if the user already has the same stock
        tot_shares = float(fetch_result[1])+float(trade_volume)
        cursor.execute(
            f'''UPDATE holdings
            SET num_shares = {tot_shares}, last_price = {last_price}
            WHERE username = "{username}" AND ticker_symbol = "{ticker_symbol}";
            '''
        )
    connection.commit()
    cursor.close()
    connection.close()


def get_user_balance(username):
    username = current_user()
    connection = sqlite3.connect('trade_information.db', check_same_thread=False)
    cursor = connection.cursor()
    query = f"SELECT current_balance FROM user WHERE username = '{username}';"
    cursor.execute(query)
    fetched_result = cursor.fetchone()
    cursor.close()
    connection.close()
    return fetched_result[0]  # cursor.fetchone() returns tuples


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
    cursor.execute(f"SELECT ticker_symbol,num_shares,last_price,date FROM transactions WHERE owner_username='{username}';")
    user_transactions = cursor.fetchall()
    cursor.close()
    connection.close()
    return user_transactions


def get_users_with_holdings():
    connection = sqlite3.connect("trade_information.db", check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("SELECT username FROM holdings WHERE username NOT LIKE 'admin'")
    users = list(cursor.fetchall())  # List of tuples
    users_list = [str(user) for user in users]  # List of strings
    cursor.close()
    connection.close()
    return users_list


def get_tkr_symb_from_holdings():
    connection = sqlite3.connect("trade_information.db", check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("SELECT ticker_symbol FROM holdings WHERE username NOT LIKE 'admin'")
    symbols = cursor.fetchall()  # List of tuples
    symbols_list = [str(sym[0]) for sym in symbols]  # List of strings
    cursor.close()
    connection.close()
    return symbols_list


def update_leaderboard():
    connection = sqlite3.connect('trade_information.db', check_same_thread=False)
    cursor = connection.cursor()
    username = get_users_with_holdings()
    for user in username:
        ticker_symbol = cursor.execute(f"SELECT ticker_symbol FROM holdings WHERE username='{user}'")
        mkt_val = cursor.execute(
            f"""SELECT (num_shares*last_price)
            FROM transactions
            WHERE owner_username = '{user}'
            AND ticker_symbol = '{ticker_symbol}';
            """
        )

        cursor.execute(
            f"""UPDATE leaderboard
            SET p_and_l={mkt_val}
            WHERE
            username='{username}'
            );"""
        )
    connection.commit()
    cursor.close()
    connection.close()


def log_out():
    connection = sqlite3.connect('trade_information.db', check_same_thread=False)
    cursor = connection.cursor()

    cursor.execute(
        """REPLACE INTO current_user(
            pk,
            username
        ) VALUES (
            1,
            'randomuser');
        """
    )
    connection.commit()
    cursor.close()
    connection.close()


def f():
    raise SystemExit(1)
