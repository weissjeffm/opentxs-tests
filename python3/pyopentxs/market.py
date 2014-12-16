import pyopentxs

BUY = False
SELL = True
MARKET_PRICE = 0


class Order:
    def __init__(self, account=None, currency_account=None, scale=None, quantity=None, price=None,
                 buy_sell=None, ttl_seconds=None):
        self.account = account
        self.currency_account = currency_account
        self.scale = scale or 1
        self.quantity = quantity
        self.price = price
        self.buy_sell = buy_sell
        self.ttl_seconds = ttl_seconds or 60 * 60 * 24  # 1 day

    def create(self):
        pyopentxs.otme.create_market_offer(self.account._id, self.currency_account._id,
                                           self.scale, 1, self.quantity, self.price, self.buy_sell,
                                           self.ttl_seconds, "", 0)
        # need to get the trans # somehow
        return self


def sell(quantity, asset_account, currency_account, price, ttl_seconds=None):
    return Order(asset_account, currency_account,
                 quantity=quantity,
                 price=price,
                 buy_sell=SELL,
                 ttl_seconds=ttl_seconds).create()


def buy(quantity, asset_account, currency_account, price, ttl_seconds=None):
    return Order(asset_account, currency_account,
                 quantity=quantity,
                 price=price,
                 buy_sell=BUY,
                 ttl_seconds=ttl_seconds).create()
