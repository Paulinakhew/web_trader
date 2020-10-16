#!/usr/bin/env python3

import sqlite3

connection = sqlite3.connect("trade_information.db", check_same_thread=False)
cursor = connection.cursor()

cursor.execute(
    """CREATE TABLE user(
        username TXT PRIMARY KEY,
        salt VARBINARY(1024),
        key VARBINARY(1024),
        current_balance FLOAT
    );"""
)

cursor.execute(
    """CREATE TABLE transactions(
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker_symbol TEXT,
        num_shares FLOAT,
        owner_username INTEGER,
        last_price FLOAT,
        date TEXT,
        FOREIGN KEY(owner_username) REFERENCES user(username)
    );"""
)

cursor.execute(
    """CREATE TABLE holdings(
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        last_price FLOAT,
        num_shares FLOAT,
        ticker_symbol VARCHAR(16),
        username VARCHAR(16),
        FOREIGN KEY (username) REFERENCES user(username)
    );"""
)

cursor.execute(
    """CREATE TABLE leaderboard(
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR,
        p_and_l FLOAT,
        FOREIGN KEY (username) REFERENCES user(username)
    );"""
)

cursor.execute(
    """CREATE TABLE current_user(
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR
    );"""
)

cursor.close()
connection.close()
