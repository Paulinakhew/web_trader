#!usr/bin/env python3
import model as m
import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
username = ''

@app.route('/',methods=['GET','POST'])
@app.route('/login',methods=['GET','POST'])
def login():
    cannot_login = None
    m.log_out()
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
            cannot_login = True
            return render_template('login.html', cannot_login=cannot_login)

@app.route('/menu',methods=['GET','POST'])
def menu():
    current_user = m.current_user()
    if request.method=="GET":
        if current_user == 'randomuser':
            return redirect('/')
        else:
            return render_template('menu.html')
    else:
        return render_template('menu.html')

@app.route('/adminmenu',methods=['GET','POST'])
def adminmenu():
    current_user = m.current_user()
    if request.method=="GET":
        if current_user != 'admin':
            return redirect('/')
        else:
            return render_template('adminmenu.html')
    else:
        return render_template('adminmenu.html')

@app.route('/create',methods=['GET','POST'])
def create():
    cannot_login = None
    if request.method=="GET":
        return render_template('create.html')
    else:
        submitted_username = request.form['username']
        submitted_password = request.form['password']
        submitted_funds = request.form['funds']
        result = m.create_(submitted_username,submitted_password,submitted_funds)
        if result == True:
            return redirect('/')
        else:
            cannot_login = True
            return render_template('create.html',cannot_login=cannot_login)

@app.route('/lookup',methods=['GET','POST'])
def look_up():
    current_user = m.current_user()
    if request.method=="GET":
        if current_user == 'randomuser':
            return redirect('/')
        else:
            return render_template('lookup.html')
    else:
        submitted_company_name=request.form['company_name']
        ticker_symb = m.lookup_ticker_symbol(submitted_company_name)
        result = "The ticker symbol for {} is {}.".format(submitted_company_name, ticker_symb)
        #result = "The last price of {} is $".format(submitted_company_name)
        return render_template('lookup.html',result=result)

@app.route('/quote',methods=['GET','POST'])
def quote():
    current_user = m.current_user()
    if request.method=="GET":
        if current_user == 'randomuser':
            return redirect('/')
        else:
            return render_template('quote.html')
    else:
        submitted_symbol=request.form['ticker_symbol']
        price = m.quote_last_price(submitted_symbol)
        result = "The last price of {} is ${}.".format(submitted_symbol, price)
        return render_template('quote.html',result=result)

@app.route('/buy',methods=['GET','POST'])
def buy():
    current_user = m.current_user()
    if request.method=="GET":
        if current_user == 'randomuser':
            return redirect('/')
        else:
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
    current_user = m.current_user()
    if request.method=="GET":
        if current_user == 'randomuser':
            return redirect('/')
        else:
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
    current_user = m.current_user()
    if request.method=="GET":
        if current_user == 'randomuser':
            return redirect('/')
        else:
            return render_template('leaderboard.html')
    else:
        return render_template('leaderboard.html')

@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    current_user = m.current_user()
    if request.method=="GET":
        if current_user == 'randomuser':
            return redirect('/')
        else:
            m.update_holdings()
            #pnl = m.calculate_p_and_l(username)
            user_holdings = m.display_user_holdings()
            #holdings = pd.DataFrame(user_holdings)
            user_transactions = m.display_user_transactions()
            return render_template('dashboard.html',position_list=user_holdings, result=user_transactions)
    else:
        return render_template('dashboard.html',result=None)

@app.route('/contact', methods=['GET','POST'])
def contact():
    current_user = m.current_user()
    if request.method=="GET":
        if current_user == 'randomuser':
            return redirect('/')
        else:
            return render_template('contact.html')
    else:
        return render_template('contact.html')

@app.route('/trade', methods=['GET','POST'])
def trade():
    current_user = m.current_user()
    if request.method=="GET":
        if current_user == 'randomuser':
            return redirect('/')
        else:
            return render_template('trade.html')
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
                return render_template('trade.html', result=result)
            else:
                return render_template('trade.html')
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
                return render_template('trade.html', results=results)
        else:
            return render_template('trade.html')

@app.route('/search', methods=['GET','POST'])
def search():
    current_user = m.current_user()
    if request.method=="GET":
        if current_user == 'randomuser':
            return redirect('/')
        else:
            return render_template('search.html')
    elif request.method=="POST":
        try:
            submitted_company_name=request.form['company_name']
            ticker_symboll = m.lookup_ticker_symbol(submitted_company_name)
            result = "The ticker symbol for {} is {}.".format(submitted_company_name, ticker_symboll)
            #result = "The last price of {} is $".format(submitted_company_name)
            return render_template('search.html',resultthree=result)
        except:
            submitted_symbol=request.form['ticker_symbol']
            price = m.quote_last_price(submitted_symbol)
            results = "The last price of {} is ${}.".format(submitted_symbol, price)
            return render_template('search.html',resultfour=results)
        else:
            return render_template('search.html')
    

if __name__ == '__main__':
    app.run(debug=True)