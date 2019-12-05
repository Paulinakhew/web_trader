#!/usr/bin/env

import json
import sqlite3
import requests
import pandas as pd
import datetime
import pytest

from unittest.mock import MagicMock  # this will be used after modularization

def current_user():
    '''Selects the username of the current user from the current_user db'''
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    query = 'SELECT username FROM current_user;'
    cursor.execute(query)
    username = cursor.fetchone()

    return username[0]

def log_in(user_name,password):
    '''Logs the user in if they exist in the user db

    Parameters:
        user_name: (str) a username mapped to a single user
        password: (str) a password belonging to the user

    Returns:
        (bool) a boolean that represents whether or not the user exists in the user db
    '''
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    query = 'SELECT count(*) FROM user WHERE username = "{}" AND password = "{}";'.format(user_name, password)
    cursor.execute(query)
    result_tuple = cursor.fetchone()

    if result_tuple[0] == 0:
        return False
    elif result_tuple[0] == 1:
        cursor.execute("UPDATE current_user SET username = '{}' WHERE pk = 1;".format(user_name))
        connection.commit()
        return True
    else:
        pass

    cursor.close()
    connection.close()

def create_(new_user,new_password,new_fund):
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()

    try:
        cursor.execute(
            """INSERT INTO user(
                username,
                password,
                current_balance
                ) VALUES(
                "{}",
                "{}",
                {}
            );""".format(new_user, new_password, new_fund)
        )
        connection.commit()
        return True
    except:
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
    #we have to search for how many of the stock we have
    #compare trade volume with how much stock we have
    #if trade_volume <= our stock, proceed
    #else return to menu
    #we need a database to save how much money we have and how much stock
    username = current_user()
    database = 'trade_information.db'
    connection = sqlite3.connect(database, check_same_thread=False)
    cursor = connection.cursor()
    query = 'SELECT count(*), num_shares FROM holdings WHERE username = "{}" AND ticker_symbol = "{}"'.format(username, ticker_symbol)
    cursor.execute(query)
    fetch_result = cursor.fetchone()

    if fetch_result[0] == 0:
        current_number_shares = 0
    else:
        current_number_shares = fetch_result[1]

    last_price = float(quote_last_price(ticker_symbol))
    brokerage_fee = 6.95 #TODO un-hardcode this value
    current_balance = get_user_balance(username) #TODO un-hardcode this value
    transaction_revenue = (trade_volume * last_price) - brokerage_fee
    agg_balance = float(current_balance) + float(transaction_revenue)
    return_list = (last_price, brokerage_fee, current_balance, trade_volume,agg_balance,username,ticker_symbol,current_number_shares)

    if current_number_shares >= trade_volume:
        return True, return_list #success
    else:
        return False, return_list
    #if yes return new balance = current balance - transaction cost

def sell_db(return_list):
    # return_list = (last_price, brokerage_fee, current_balance, trade_volume, agg_balance, username, ticker_symbol, current_number_shares)
    #check if user holds enough stock
    #update user's balance
    #insert transaction
    #if user sold all stocks holdings row should be deleted not set to 0
    database = 'trade_information.db'
    connection = sqlite3.connect(database,check_same_thread = False)
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

    #user
    cursor.execute("""
        UPDATE user
        SET current_balance = {}
        WHERE username = '{}';
    """.format(agg_balance, username)
    )

    #transactions
    cursor.execute("""
        INSERT INTO transactions(
        ticker_symbol,
        num_shares,
        owner_username,
        last_price,
        date
        ) VALUES(
        '{}',{},'{}',{}, '{}'
        );""".format(ticker_symbol, trade_volume*-1, username, last_price, date)
    )

    #holdings
    #at this point, it it assumed that the user has enough shares to sell.
    if current_number_shares >= trade_volume: #if user isn't selling all shares of a specific company
        tot_shares = float(current_number_shares)-float(trade_volume)
        cursor.execute('''
            UPDATE holdings
            SET num_shares = {}, last_price = {}
            WHERE username = "{}" AND ticker_symbol = "{}";
        '''.format(tot_shares, last_price, username, ticker_symbol)
        )

    connection.commit()
    cursor.close()
    connection.close()

def buy(username, ticker_symbol, trade_volume):
    #we need to return True or False for the confirmation message
    trade_volume = float(trade_volume)
    last_price = float(quote_last_price(ticker_symbol))
    brokerage_fee = 6.95 #TODO un-hardcode this value
    username = current_user()
    current_balance = get_user_balance(username)
    #TODO: un-hardcode this value
    transaction_cost = (trade_volume * last_price) + brokerage_fee
    left_over = float(current_balance) - float(transaction_cost)
    return_list = (last_price, brokerage_fee, current_balance, trade_volume,left_over,username,ticker_symbol)
    if transaction_cost <= current_balance:
        return True, return_list #success
    else:
        return False, return_list
    #if yes return new balance = current balance - transaction cost

def buy_db(return_list): # return_list = (last_price, brokerage_fee, current_balance, trade_volume, left_over, username, ticker_symbol)
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    database = 'trade_information.db'
    username = current_user()
    connection = sqlite3.connect(database,check_same_thread = False)
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

    #update users(current_balance), stocks, holdings.
    #users
        #updating the balance of the user
    cursor.execute("""
        UPDATE user
        SET current_balance = {}
        WHERE username = '{}';
    """.format(left_over, username)
    )
    #transactions
    cursor.execute("""
        INSERT INTO transactions(
        ticker_symbol,
        num_shares,
        owner_username,
        last_price,
        date
        ) VALUES(
        '{}',{},'{}',{},'{}'
        );""".format(ticker_symbol,trade_volume,username,last_price,date)
    )

    #inserting information
    #holdings
    query = 'SELECT count(*), num_shares FROM holdings WHERE username = "{}" AND ticker_symbol = "{}"'.format(username, ticker_symbol)
    cursor.execute(query)
    fetch_result = cursor.fetchone()
    if fetch_result[0] == 0: #if the user didn't own the specific stock
        cursor.execute('''
            INSERT INTO holdings(last_price, num_shares, ticker_symbol, username)
            VALUES (
            {},{},"{}","{}"
            );'''.format(last_price, trade_volume, ticker_symbol, username)
        )
    else: #if the user already has the same stock
        tot_shares = float(fetch_result[1])+float(trade_volume)
        cursor.execute('''
            UPDATE holdings
            SET num_shares = {}, last_price = {}
            WHERE username = "{}" AND ticker_symbol = "{}";
        '''.format(tot_shares, last_price, username, ticker_symbol)
        )
    connection.commit()
    cursor.close()
    connection.close()

def get_user_balance(username):
    username = current_user()
    connection = sqlite3.connect('trade_information.db', check_same_thread = False)
    cursor = connection.cursor()
    query = 'SELECT current_balance FROM user WHERE username = "{}";'.format(username)
    cursor.execute(query)
    fetched_result = cursor.fetchone()
    cursor.close()
    connection.close()
    return fetched_result[0] #cursor.fetchone() returns tuples

def lookup_ticker_symbol(company_name):
    endpoint = 'http://dev.markitondemand.com/MODApis/Api/v2/Lookup/json?input='+company_name
    #FIXME The following return statement assumes that only one
    #ticker symbol will be matched with the user's input.
    #FIXME There also isn't any error handling.
    return json.loads(requests.get(endpoint).text)[0]['Symbol']

def quote_last_price(ticker_symbol):
    endpoint = 'http://dev.markitondemand.com/MODApis/Api/v2/Quote/json?symbol='+ticker_symbol
    return json.loads(requests.get(endpoint).text)['LastPrice']

def display_user_holdings():
    username=current_user()
    connection = sqlite3.connect("trade_information.db", check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("SELECT ticker_symbol,num_shares,last_price FROM holdings WHERE username='{}';".format(username))
    user_holdings = cursor.fetchall()
    cursor.close()
    connection.close()
    return user_holdings

def display_user_transactions():
    username=current_user()
    connection = sqlite3.connect("trade_information.db", check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("SELECT ticker_symbol,num_shares,last_price,date FROM transactions WHERE owner_username='{}';".format(username))
    user_transactions = cursor.fetchall()
    cursor.close()
    connection.close()
    return user_transactions

def get_users_with_holdings():
    connection = sqlite3.connect("trade_information.db", check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("SELECT username FROM holdings WHERE username NOT LIKE 'admin'")
    users = list(cursor.fetchall()) # List of tuples
    users_list = [str(user) for user in users] # List of strings
    cursor.close()
    connection.close()
    return users_list

def get_tkr_symb_from_holdings():
    connection = sqlite3.connect("trade_information.db", check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("SELECT ticker_symbol FROM holdings WHERE username NOT LIKE 'admin'")
    symbols = cursor.fetchall() # List of tuples
    symbols_list = [str(sym[0]) for sym in symbols] # List of strings
    cursor.close()
    connection.close()
    return symbols_list

def update_leaderboard():
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    username = get_users_with_holdings()
    for user in username:
        ticker_symbol = cursor.execute('SELECT ticker_symbol FROM holdings WHERE username="{}"'.format(user))
        mkt_val = cursor.execute("SELECT (num_shares*last_price) FROM transactions WHERE owner_username = '{}' AND ticker_symbol = '{}';".format(user,ticker_symbol))
        cursor.execute("""
            UPDATE leaderboard
            SET p_and_l={}
            WHERE
            username='{}'
            );""".format(mkt_val, username)
        )
    connection.commit()
    cursor.close()
    connection.close()

def log_out():
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()

    cursor.execute(
    """REPLACE INTO current_user(
        pk,
        username
    ) VALUES(
        1,
        '{}'
    );""".format(
        'randomuser'
        )
    )
    connection.commit()
    cursor.close()
    connection.close()
