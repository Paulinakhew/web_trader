
# leaderboard()
#    username = current_user()
#    symbols=cursor.execute("SELECT ticker_symbol FROM holdings WHERE user='{}'".format(username))
#    for symbol in symbols:
#        last_sale = float(quote_last_price(symbol))
#         select num_shares per symbol
#        shares = cursor.execute("SELECT num_shares FROM holdings WHERE ticker_symbol='{}'".format(symbol))
#        profit = last_sale


'''def leaderboard():
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    usernames = get_users_with_holdings()
    ticker_symbols = get_tkr_symb_from_holdings()
    for user in usernames:
        ticker_symbol = cursor.execute('SELECT ticker_symbol FROM holdings WHERE username="{}"'.format(user))
        mkt_val = cursor.execute("SELECT (num_shares*last_price) FROM transactions WHERE owner_username = '{}' AND ticker_symbol = '{}';".format(user,ticker_symbol))
        cursor.execute("""
            INSERT INTO leaderboard(username, p_and_l)
            VALUES(
            '{}',{}
            );""".format(user, mkt_val)
        )
    connection.commit()
    cursor.close()
    connection.close()
'''


'''def calculate_p_and_l():
    username = current_user()
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    database = 'trade_information.db'

    #getting all ticker symbols for current user
    all_ticker_symbols = 'SELECT ticker_symbol FROM holdings WHERE username = "{}"'.format(username)
    cursor.execute(all_ticker_symbols)
    tksmb = cursor.fetchall()
    ticker_symbols = [str(symb) for symb in tksmb] # List of strings
    p_and_l= 0
    for symbol in ticker_symbols:
        stock_transactions = 'SELECT * FROM transactions WHERE owner_username = "{}" and ticker_symbol = "{}"'.format(username, symbol)
        cursor.execute(stock_transactions)
        transactions = cursor.fetchall()
        total_shares = 0
        price = 0
# do this instead
# SELECT sum(num_shares*last_price) from transactions where owner_username = 'John' AND ticker_symbol = 'x';
        for transaction in transactions:
            ticker_symbol = transaction[1]
            trade_volume = transaction[2]
            username = transaction[3]
            last_price = transaction[4]

            shares = 'SELECT num_shares FROM holdings WHERE username = "{}" AND ticker_symbol = "{}"'.format(username, symbol)
            cursor.execute(shares)
            nshares = cursor.fetchall()
            num_shares = [float(num[0]) for num in list(nshares)]

            total_shares += sum(num_shares)

            for shares in num_shares:
                purchased_price = 'SELECT last_price FROM transactions WHERE owner_username = "{}" AND ticker_symbol = "{}" AND num_shares = {}'.format(username, symbol, shares)
                cursor.execute(purchased_price)
                purchased_price = cursor.fetchall()
                purchase_price = [float(price[0]) for price in purchased_price]
                price += shares * purchase_price
    p_and_l += price/total_shares
    return p_and_l
'''


# def calculate_balance(ticker_symbol, trade_volume):
#     connection = sqlite3.connect('trade_information.db',check_same_thread=False)
#     cursor = connection.cursor()
#     database = 'trade_information.db'

#     #current_balance = 1000.0 #TODO un-hardcode this value
#     last_price = float(quote_last_price(ticker_symbol))
#     brokerage_fee = 6.95 #TODO un-hardcode this value
#     transaction_cost = (trade_volume * last_price) + brokerage_fee
#     new_balance = current_balance - transaction_cost
#     return new_balance