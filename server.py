from flask_jsonpify import jsonpify
from flask_restful import Resource
from sqlalchemy import create_engine

db_connect = create_engine("sqlite:///trade_information.db")


class Users(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute("Select username, current_balance from user;")
        return jsonpify({"users": query.cursor.fetchall()})


class Transactions(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute(
            "Select owner_username, ticker_symbol, last_price, num_shares from transactions;"
        )
        return jsonpify({"transactions": query.cursor.fetchall()})


class UserTransactions(Resource):
    def get(self, username):
        conn = db_connect.connect()
        query = conn.execute(
            f"Select ticker_symbol, last_price, num_shares from transactions where owner_username='{username}';"
        )
        return jsonpify({f"{username}'s transactions": query.cursor.fetchall()})


class UserHoldings(Resource):
    def get(self, username):
        conn = db_connect.connect()
        query = conn.execute(
            f"Select ticker_symbol, last_price, num_shares from holdings where username='{username}';"
        )
        return jsonpify({f"{username}'s holdings": query.cursor.fetchall()})
