class Transaction():
    '''Class to store information about a single transaction'''
    def __init__(
        self,
        username,
        last_price,
        brokerage_fee,
        current_balance,
        trade_volume,
        left_over,
        ticker_symbol,
    ):
        self.username = username
        self.last_price = last_price
        self.brokerage_fee = brokerage_fee
        self.current_balance = current_balance
        self.trade_volume = trade_volume
        self.left_over = left_over
        self.ticker_symbol = ticker_symbol

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
