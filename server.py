from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask_jsonpify import jsonpify

db_connect = create_engine('sqlite:///trade_information.db')


class Users(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute("Select username, current_balance from user;")
        return {'users': query.cursor.fetchall()}
