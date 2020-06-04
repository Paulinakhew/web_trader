from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask_jsonpify import jsonpify

db_connect = create_engine('sqlite:///trade_information.db')


class Users(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute('Select username, current_balance from user;')
        return {'users': query.cursor.fetchall()}


class Transactions(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute('Select owner_username, ticker_symbol, last_price, num_shares from transactions;')
        return {'transactions': query.cursor.fetchall()}


class UserTransactions(Resource):
    def get(self, username):
        conn = db_connect.connect()
        query = conn.execute(
            f"Select ticker_symbol, last_price, num_shares from transactions where owner_username='{username}';"
        )
        return {f"{username}'s transactions": query.cursor.fetchall()} if query.cursor.fetchall() else None
