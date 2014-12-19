from pyopentxs.tests import data
import pyopentxs
import pytest
import time
import opentxs
from pyopentxs import market

cron_interval = 10


@pytest.fixture
def marketaccounts():
    marketaccounts = data.MarketAccounts()
    marketaccounts.initial_balance()
    return marketaccounts


def assert_balances(*acct_balances):
    '''Takes a tuple of (account, balance) where account is an Account
       object and balance is the integer balance that the account is
       expected to have.

    '''
    for (acct, bal) in acct_balances:
        assert(acct.balance() == bal)


@pytest.mark.parametrize(
    "sell_quantity,sell_price,buy_quantity,buy_price,seller_exp_bal1,"
    "seller_exp_bal2,buyer_exp_bal1,buyer_exp_bal2",
    [[3, 7, 3, 7, 97, 121, 103, 79],  # basic

     pytest.mark.skipif(True, reason="https://github.com/Open-Transactions/opentxs/issues/504")
     ([0, 7, 3, 7, 100, 100, 100, 100]),  # order for 0 quantity is noop

     [5, 20, 5, 20, 95, 200, 105, 0],  # buy w all currency
     [100, 1, 100, 1, 0, 200, 200, 0],  # sell all
     [100, 7, 20, 7, 86, 198, 114, 2]]  # buy limited by available funds
)
def test_immediate_trade(marketaccounts, sell_quantity, sell_price, buy_quantity, buy_price,
                         seller_exp_bal1, seller_exp_bal2, buyer_exp_bal1, buyer_exp_bal2):
    '''Create two offers at the same price so that the trade should
       execute immediately.'''
    alice = marketaccounts.alice
    bob = marketaccounts.bob

    market.sell(sell_quantity, alice.account1, alice.account2, price=sell_price)
    market.buy(buy_quantity, bob.account1, bob.account2, price=buy_price)

    time.sleep(cron_interval)
    assert_balances((alice.account1, seller_exp_bal1),
                    (alice.account2, seller_exp_bal2),
                    (bob.account1, buyer_exp_bal1),
                    (bob.account2, buyer_exp_bal2))


def test_bid_market_price(marketaccounts):
    '''Test that a bid at market price takes the existing orders correctly'''
    alice = marketaccounts.alice
    bob = marketaccounts.bob

    market.sell(3, alice.account1, alice.account2, price=7)
    market.sell(3, alice.account1, alice.account2, price=8)
    market.buy(4, bob.account1, bob.account2, price=market.MARKET_PRICE)

    time.sleep(cron_interval)
    assert_balances((alice.account1, 96),
                    (alice.account2, 129),  # 3 at 7 and 1 at 8
                    (bob.account1, 104),
                    (bob.account2, 71))


def test_ask_market_price(marketaccounts):
    '''Test that an ask at market price takes the existing orders correctly'''
    alice = marketaccounts.alice
    bob = marketaccounts.bob

    market.buy(3, bob.account1, bob.account2, price=7)
    market.buy(3, bob.account1, bob.account2, price=8)
    market.sell(4, alice.account1, alice.account2, price=market.MARKET_PRICE)

    time.sleep(cron_interval)
    assert_balances((alice.account1, 96),
                    (alice.account2, 131),  # 3 at 8 and 1 at 7
                    (bob.account1, 104),
                    (bob.account2, 69))


def test_market_offers_buying(marketaccounts):
    alice = marketaccounts.alice
    bob = marketaccounts.bob

    market.buy(3, bob.account1, bob.account2, price=7)

    time.sleep(cron_interval)
    server_id = bob.account1.server_id

    message = pyopentxs.otme.get_market_list(server_id, alice.account1.nym._id)
    assert pyopentxs.is_message_success(message)

    obj = opentxs.QueryObject(opentxs.STORED_OBJ_MARKET_LIST, "markets",
                              server_id, "market_data.bin")
    market_list = opentxs.MarketList_ot_dynamic_cast(obj)
    market_data_count = market_list.GetMarketDataCount()
    assert market_data_count >= 1
    market_data = [market_list.GetMarketData(m) for m in range(market_data_count)]
    matching_markets = list(filter(lambda m: (bob.account1.asset._id == m.instrument_definition_id
                                              and bob.account2.asset._id == m.currency_type_id),
                                   market_data))
    assert len(matching_markets) == 1
    c = matching_markets[0]

    assert bob.account1.asset._id == c.instrument_definition_id
    assert bob.account2.asset._id == c.currency_type_id
    assert '1' == c.scale
    assert '0' == c.total_assets
    assert '1' == c.number_bids
    assert '0' == c.number_asks
    assert '1' == c.last_sale_price
    assert '7' == c.current_bid
    assert '0' == c.current_ask
    assert '0' == c.volume_trades
    assert '0' == c.volume_assets
    assert '0' == c.volume_currency
    assert '0' == c.recent_highest_bid
    assert '0' == c.recent_lowest_ask
    assert '' == c.last_sale_date

    message = pyopentxs.otme.get_market_offers(server_id, alice.account1.nym._id, c.market_id, 20)
    assert pyopentxs.is_message_success(message)

    obj = opentxs.QueryObject(opentxs.STORED_OBJ_OFFER_LIST_MARKET, "markets",
                              server_id, c.market_id + ".bin")
    tradeList = opentxs.OfferListMarket_ot_dynamic_cast(obj)
    assert 0 == tradeList.GetAskDataCount()
    assert 1 == tradeList.GetBidDataCount()

    c = tradeList.GetBidData(0)

    assert '' == c.gui_label
#    assert '' == c.transaction_id
#    assert '' == c.date
    assert '7' == c.price_per_scale
    assert '3' == c.available_assets
    assert '1' == c.minimum_increment


def test_market_offers_selling(marketaccounts):
    alice = marketaccounts.alice
    bob = marketaccounts.bob

    market.sell(3, bob.account1, bob.account2, price=7)

    time.sleep(cron_interval)
    server_id = bob.account1.server_id

    message = pyopentxs.otme.get_market_list(server_id, alice.account1.nym._id)
    assert pyopentxs.is_message_success(message)

    obj = opentxs.QueryObject(opentxs.STORED_OBJ_MARKET_LIST, "markets", server_id,
                              "market_data.bin")

    market_list = opentxs.MarketList_ot_dynamic_cast(obj)
    market_data_count = market_list.GetMarketDataCount()
    assert market_data_count >= 1
    market_data = [market_list.GetMarketData(m) for m in range(market_data_count)]
    matching_markets = list(filter(lambda m: (bob.account1.asset._id == m.instrument_definition_id
                                              and bob.account2.asset._id == m.currency_type_id),
                                   market_data))
    assert len(matching_markets) == 1
    c = matching_markets[0]

    assert bob.account1.asset._id == c.instrument_definition_id
    assert bob.account2.asset._id == c.currency_type_id
    assert '1' == c.scale
    assert '3' == c.total_assets
    assert '0' == c.number_bids
    assert '1' == c.number_asks
    assert '1' == c.last_sale_price
    assert '0' == c.current_bid
    assert '7' == c.current_ask
    assert '0' == c.volume_trades
    assert '0' == c.volume_assets
    assert '0' == c.volume_currency
    assert '0' == c.recent_highest_bid
    assert '0' == c.recent_lowest_ask
    assert '' == c.last_sale_date

    message = pyopentxs.otme.get_market_offers(server_id, alice.account1.nym._id, c.market_id, 20)
    assert pyopentxs.is_message_success(message)

    obj = opentxs.QueryObject(opentxs.STORED_OBJ_OFFER_LIST_MARKET, "markets", server_id,
                              c.market_id + ".bin")
    tradeList = opentxs.OfferListMarket_ot_dynamic_cast(obj)
    assert 1 == tradeList.GetAskDataCount()
    assert 0 == tradeList.GetBidDataCount()

    c = tradeList.GetAskData(0)

    assert '' == c.gui_label
#    assert '' == c.transaction_id
    assert '7' == c.price_per_scale
    assert '3' == c.available_assets
    assert '1' == c.minimum_increment
#    assert '' == c.date


def test_get_nym_market_offers_selling(marketaccounts):
    alice = marketaccounts.alice
    bob = marketaccounts.bob
    server_id = bob.account1.server_id

    market.sell(3, bob.account1, bob.account2, price=7)

    time.sleep(cron_interval)

    message = pyopentxs.otme.get_nym_market_offers(server_id, bob.nym._id)
    assert pyopentxs.is_message_success(message)

    obj = opentxs.QueryObject(opentxs.STORED_OBJ_OFFER_LIST_NYM, "nyms", server_id,
                              bob.nym._id + ".bin")
    offerList = opentxs.OfferListNym_ot_dynamic_cast(obj)
    assert 1 == offerList.GetOfferDataNymCount()
    
    c = offerList.GetOfferDataNym(0)

    assert "" == c.gui_label
#    assert "" == c.valid_from
#    assert "" == c.valid_to
    assert server_id == c.notary_id
    assert bob.account1.asset._id == c.instrument_definition_id
    assert bob.account1._id == c.asset_acct_id
    assert bob.account2.asset._id == c.currency_type_id
    assert bob.account2._id == c.currency_acct_id
    assert True == c.selling
    assert "1" == c.scale
    assert "7" == c.price_per_scale
#    assert "" == c.transaction_id
    assert "3" == c.total_assets
    assert "0" == c.finished_so_far
    assert "1" == c.minimum_increment
    assert "" == c.stop_sign
    assert "0" == c.stop_price
#    assert "" == c.date


def test_get_nym_market_offers_buying(marketaccounts):
    alice = marketaccounts.alice
    bob = marketaccounts.bob
    server_id = bob.account1.server_id

    market.buy(3, bob.account1, bob.account2, price=7)

    time.sleep(cron_interval)

    message = pyopentxs.otme.get_nym_market_offers(server_id, bob.nym._id)
    assert pyopentxs.is_message_success(message)

    obj = opentxs.QueryObject(opentxs.STORED_OBJ_OFFER_LIST_NYM, "nyms", server_id,
                              bob.nym._id + ".bin")
    offerList = opentxs.OfferListNym_ot_dynamic_cast(obj)
    assert 1 == offerList.GetOfferDataNymCount()
    
    c = offerList.GetOfferDataNym(0)

    assert "" == c.gui_label
#    assert "" == c.valid_from
#    assert "" == c.valid_to
    assert server_id == c.notary_id
    assert bob.account1.asset._id == c.instrument_definition_id
    assert bob.account1._id == c.asset_acct_id
    assert bob.account2.asset._id == c.currency_type_id
    assert bob.account2._id == c.currency_acct_id
    assert False == c.selling
    assert "1" == c.scale
    assert "7" == c.price_per_scale
#    assert "" == c.transaction_id
    assert "3" == c.total_assets
    assert "0" == c.finished_so_far
    assert "1" == c.minimum_increment
    assert "" == c.stop_sign
    assert "0" == c.stop_price
#    assert "" == c.date
