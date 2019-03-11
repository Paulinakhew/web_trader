#!usr/bin/env python3
import model as m
import time
import os
import sqlite3
#import pandas as pd
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
username = ''

@app.route('/',methods=['GET'])
def redirect_to_login():
    if request.method=="GET":
        return redirect('/login')
    else:
        return redirect('/login')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=="GET":
        return render_template('login.html')
    else:
        submitted_username= request.form['username']
        submitted_password = request.form['password']
        result = m.log_in(submitted_username,submitted_password)
        if result == True:
            username = submitted_username
            if username=='admin':
                return redirect('/adminmenu')
            else:
                return redirect('/menu')
        else:
            return redirect('/login')


@app.route('/menu',methods=['GET','POST'])
def mainmenu():
    if request.method=="GET":
        return render_template('menu.html')
    else:
        return render_template('menu.html')


@app.route('/adminmenu',methods=['GET','POST'])
def adminmenu():
    if request.method=="GET":
        return render_template('adminmenu.html')
    else:
        return render_template('adminmenu.html')


@app.route('/create',methods=['GET','POST'])
def create():
    if request.method=="GET":
        return render_template('create.html')
    else:
        submitted_username = request.form['username']
        submitted_password = request.form['password']
        submitted_funds = request.form['funds']
        result = m.create_(submitted_username,submitted_password,submitted_funds)
        return redirect('/login')

@app.route('/lookup',methods=['GET','POST'])
def look_up():
    if request.method=="GET":
        return render_template('lookup.html')
    else:
        submitted_company_name=request.form['company_name']
        ticker_symb = m.lookup_ticker_symbol(submitted_company_name)
        result = "The ticker symbol for {} is {}.".format(submitted_company_name, ticker_symb)
        #result = "The last price of {} is $".format(submitted_company_name)
        return render_template('lookup.html',result=result)

@app.route('/quote',methods=['GET','POST'])
def quote():
    if request.method=="GET":
        return render_template('quote.html')
    else:
        submitted_symbol=request.form['ticker_symbol']
        price = m.quote_last_price(submitted_symbol)
        result = "The last price of {} is ${}.".format(submitted_symbol, price)
        return render_template('quote.html',result=result)

# TODO app.route trade should do both buys and sells
# @app.route('/trade',methods=['GET','POST'])
# def buy():
#    if request.method=="GET":
#        return render_template('trade.html')
#    else:
#       pass

@app.route('/buy',methods=['GET','POST'])
def buy():
#    username = m.current_user()
    if request.method=="GET":
        return render_template('buy.html')
    else:
        submitted_symbol=request.form['ticker_symbol']
        submitted_volume=request.form['number_of_shares']
        submitted_volume = int(submitted_volume)
        confirmation_message, return_list = m.buy(username,submitted_symbol,submitted_volume)
        result = "You bought {} shares of {}.".format(submitted_volume, submitted_symbol)
        m.update_holdings()
        if confirmation_message == True:
            m.buy_db(return_list)
            return render_template('buy.html', result=result)
        else:
            return render_template('buy.html')

@app.route('/sell',methods=['GET','POST'])
def sell():
    if request.method=="GET":
        return render_template('sell.html')
    else:
        submitted_symbol=request.form['ticker_symbol']
        submitted_volume=request.form['number_of_shares']
        submitted_volume = int(submitted_volume)
        confirmation_message, return_list = m.sell(username,submitted_symbol,submitted_volume)
        result = "You sold {} shares of {}.".format(submitted_volume, submitted_symbol)
        m.update_holdings()
        if confirmation_message == True:
            m.sell_db(return_list)
            return render_template('sell.html', result=result)
        else:
            return render_template('sell.html')

@app.route('/leaderboard',methods=['GET','POST'])
def leaderboard():
    if request.method=="GET":
        return render_template('leaderboard.html')
    else:
        return render_template('leaderboard.html')

@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    if request.method=="GET":
        #pnl = m.calculate_p_and_l(username)
        user_holdings = m.display_user_holdings()
        #holdings = pd.DataFrame(user_holdings)
        user_transactions = m.display_user_transactions()
        return render_template('dashboard.html',position_list=user_holdings, result=user_transactions)
    else:
        return render_template('dashboard.html',result=result)


@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method=="GET":
        return render_template('contact.html')
    else:
        return render_template('contact.html')

@app.route('/bs', methods=['GET','POST'])
def buyandsell():
    if request.method=="GET":
        return render_template('bs.html')
    elif request.method=="POST":
        try:
            submitted_symbol=request.form['ticker_symbol']
            submitted_volume=request.form['number_of_shares']
            submitted_volume = int(submitted_volume)
            confirmation_message, return_list = m.buy(username,submitted_symbol,submitted_volume)
            result = "You bought {} shares of {}.".format(submitted_volume, submitted_symbol)
            m.update_holdings()
            if confirmation_message == True:
                m.buy_db(return_list)
                return render_template('bs.html', result=result)
            else:
                return render_template('bs.html')
    #elif request.method=="POST":
        except:
            submitted_symbols=request.form['ticker_symb']
            submitted_volumes=request.form['number_shares']
            submitted_volumes= int(submitted_volumes)
            confirmation_message, return_list = m.sell(username,submitted_symbols,submitted_volumes)
            results = "You sold {} shares of {}.".format(submitted_volumes, submitted_symbols)
            m.update_holdings()
            if confirmation_message == True:
                m.sell_db(return_list)
                return render_template('bs.html', results=results)
        else:
            return render_template('bs.html')

@app.route('/lq', methods=['GET','POST'])
def lookupquote():
    if request.method=="GET":
        return render_template('lq.html')
    elif request.method=="POST":
        try:
            submitted_company_name=request.form['company_name']
            ticker_symboll = m.lookup_ticker_symbol(submitted_company_name)
            result = "The ticker symbol for {} is {}.".format(submitted_company_name, ticker_symboll)
            #result = "The last price of {} is $".format(submitted_company_name)
            return render_template('lq.html',resultthree=result)
        except:
            submitted_symbol=request.form['ticker_symbol']
            price = m.quote_last_price(submitted_symbol)
            results = "The last price of {} is ${}.".format(submitted_symbol, price)
            return render_template('lq.html',resultfour=results)
        else:
            return render_template('lq.html')
    

if __name__ == '__main__':
    app.run(debug=True)
