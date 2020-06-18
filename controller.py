#!usr/bin/env python3
import model as m
from flask import Flask, render_template, request, redirect
from flask_restx import Api
from server import Users, Transactions, UserTransactions, UserHoldings


app = Flask(__name__)
username = ''

api = Api(
    app=app,
    title='Web Trader API',
    description='Endpoints used to track users, transactions, and holdings',
    doc='/docs',
    default='App Details',
    default_label='Contains all API endpoints'
)

api.add_resource(Users, '/users')
api.add_resource(Transactions, '/transactions')
api.add_resource(UserTransactions, '/transactions/<username>')
api.add_resource(UserHoldings, '/holdings/<username>')


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    cannot_login = None
    m.log_out()
    if request.method == "GET":
        return render_template('login.html')
    else:
        submitted_username = request.form['username']
        submitted_password = request.form['password']
        result = m.log_in(submitted_username, submitted_password)
        if result:
            return redirect('/menu')
        else:
            cannot_login = True
            return render_template('login.html', cannot_login=cannot_login)


@app.route('/menu', methods=['GET', 'POST'])
def menu():
    current_user = m.current_user()
    if request.method == "GET":
        if current_user == 'randomuser':
            return redirect('/login')
        else:
            return render_template('menu.html')
    else:
        return render_template('menu.html')


@app.route('/create', methods=['GET', 'POST'])
def create():
    cannot_create = None
    if request.method == "GET":
        return render_template('create.html')
    else:
        submitted_username = request.form['username']
        submitted_password = request.form['password']
        submitted_funds = request.form['funds']
        result = m.create_(
            submitted_username,
            submitted_password,
            submitted_funds
        )
        if result:
            return redirect('/login')
        else:
            cannot_create = True
            return render_template('create.html', cannot_create=cannot_create)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    current_user = m.current_user()
    if request.method == "GET":
        if current_user == 'randomuser':
            return redirect('/login')
        else:
            m.update_holdings()
            # pnl = m.calculate_p_and_l(username)
            user_holdings = m.display_user_holdings()
            # holdings = pd.DataFrame(user_holdings)
            user_transactions = m.display_user_transactions()
            return render_template(
                'dashboard.html',
                position_list=user_holdings,
                result=user_transactions
            )
    else:
        return render_template('dashboard.html', result=None)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    current_user = m.current_user()
    if request.method == "GET":
        if current_user == 'randomuser':
            return redirect('/login')
        else:
            return render_template('contact.html')
    else:
        return render_template('contact.html')


@app.route('/trade', methods=['GET', 'POST'])
def trade():
    current_user = m.current_user()
    if request.method == "GET":
        if current_user == 'randomuser':
            return redirect('/login')
        else:
            return render_template('trade.html')
    elif request.method == "POST":
        try:
            submitted_symbol = request.form['ticker_symbol'].upper()
            submitted_volume = request.form['number_of_shares']
            submitted_volume = int(submitted_volume)
            confirmation_message, transaction = m.buy(
                username,
                submitted_symbol,
                submitted_volume
            )
            if submitted_volume == 1:
                result = "You bought {} share of {}.".format(
                    submitted_volume,
                    submitted_symbol
                )
            else:
                result = "You bought {} shares of {}.".format(
                    submitted_volume,
                    submitted_symbol
                )
            m.update_holdings()
            if confirmation_message:
                m.buy_db(transaction)
                return render_template('trade.html', result=result)
            else:
                return render_template('trade.html')
        except:
            submitted_symbols = request.form['ticker_symb'].upper()
            submitted_volumes = request.form['number_shares']
            submitted_volumes = int(submitted_volumes)
            confirmation_message, transaction = m.sell(
                username,
                submitted_symbols,
                submitted_volumes
            )
            if submitted_volumes == 1:
                results = "You sold {} share of {}.".format(
                    submitted_volumes,
                    submitted_symbols
                )
            else:
                results = "You sold {} shares of {}.".format(
                    submitted_volumes,
                    submitted_symbols
                )
            m.update_holdings()
            if confirmation_message:
                m.sell_db(transaction)
                return render_template('trade.html', results=results)
            else:
                return render_template('trade.html', cannot_sell=True)


@app.route('/search', methods=['GET', 'POST'])
def search():
    current_user = m.current_user()
    if request.method == "GET":
        if current_user == 'randomuser':
            return redirect('/login')
        else:
            return render_template('search.html')
    elif request.method == "POST":
        try:
            submitted_company_name = request.form['company_name']
            submitted_company_name = submitted_company_name.capitalize()
            ticker_symboll = m.lookup_ticker_symbol(submitted_company_name)
            result = "The ticker symbol for {} is {}.".format(
                submitted_company_name,
                ticker_symboll
            )
            return render_template('search.html', resultthree=result)
        except:
            submitted_symbol = request.form['ticker_symbol']
            submitted_symbol = submitted_symbol.upper()
            price = m.quote_last_price(submitted_symbol)
            results = "The last price of {} is ${}.".format(
                submitted_symbol,
                price
            )
            return render_template('search.html', resultfour=results)
        else:
            return render_template('search.html')


if __name__ == '__main__':
    app.run(debug=True)
