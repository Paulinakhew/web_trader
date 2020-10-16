class Transaction:
    """Class to store information about a single transaction

    Parameters:
        last_price (float): a float representing the last opened price of the stock
        brokerage_fee (float): the fee for performing a transaction
        current_balance (float): the user's current balance
        trade_volume (int): the amount of stock the user intends to purchase/sell
        new_balance (float): the balance after the transaction is executed
        ticker_symbol (str): a string representing the ticker symbol of the stock
        current_number_shares (float): the current number of shares the user owns
    """

    def __init__(
        self,
        last_price,
        brokerage_fee,
        current_balance,
        trade_volume,
        new_balance,
        ticker_symbol,
        current_number_shares,
    ):
        self.last_price = last_price
        self.brokerage_fee = brokerage_fee
        self.current_balance = current_balance
        self.trade_volume = trade_volume
        self.new_balance = new_balance
        self.ticker_symbol = ticker_symbol
        self.current_number_shares = current_number_shares

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
