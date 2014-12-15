from pyopentxs.tests import data
import pyopentxs
import pytest
import time
import opentxs

cron_interval = 30


@pytest.fixture
def marketaccounts():
    marketaccounts = data.MarketAccounts()
    marketaccounts.initial_balance()
    return marketaccounts


def test_immediate_trade(marketaccounts):
    '''Create two offers at the same price so that the trade should
       execute immediately.'''
    alice = marketaccounts.alice
    bob = marketaccounts.bob
    pyopentxs.otme.create_market_offer(alice.account1._id, alice.account2._id,
                                       1, 1, 3, 7, True, 10000, "", 0)
    pyopentxs.otme.create_market_offer(bob.account1._id, bob.account2._id,
                                       1, 1, 3, 7, False, 10000, "", 0)
    time.sleep(cron_interval)
    assert(alice.account1.balance() == 97)
    assert(alice.account2.balance() == 121)
    assert(bob.account1.balance() == 103)
    assert(bob.account2.balance() == 79)


def test_bid_market_price(marketaccounts):
    '''Test that a bid at market price takes the existing orders correctly'''
    alice = marketaccounts.alice
    bob = marketaccounts.bob
    pyopentxs.otme.create_market_offer(alice.account1._id, alice.account2._id,
                                       1, 1, 3, 7, True, 10000, "", 0)
    pyopentxs.otme.create_market_offer(alice.account1._id, alice.account2._id,
                                       1, 1, 3, 8, True, 10000, "", 0)
    pyopentxs.otme.create_market_offer(bob.account1._id, bob.account2._id,
                                       1, 1, 4, 0, False, 10000, "", 0)
    time.sleep(cron_interval)
    assert(alice.account1.balance() == 96)
    assert(alice.account2.balance() == 129)  # 3 at 7 and 1 at 8
    assert(bob.account1.balance() == 104)
    assert(bob.account2.balance() == 71)


def test_ask_market_price(marketaccounts):
    '''Test that an ask at market price takes the existing orders correctly'''
    alice = marketaccounts.alice
    bob = marketaccounts.bob
    pyopentxs.otme.create_market_offer(bob.account1._id, bob.account2._id,
                                       1, 1, 3, 7, False, 10000, "", 0)
    pyopentxs.otme.create_market_offer(bob.account1._id, bob.account2._id,
                                       1, 1, 3, 8, False, 10000, "", 0)
    pyopentxs.otme.create_market_offer(alice.account1._id, alice.account2._id,
                                       1, 1, 4, 0, True, 10000, "", 0)
    time.sleep(cron_interval)
    assert(alice.account1.balance() == 96)
    assert(alice.account2.balance() == 131)  # 3 at 8 and 1 at 7
    assert(bob.account1.balance() == 104)
    assert(bob.account2.balance() == 69)


def test_market_offers_buying(marketaccounts):
    alice = marketaccounts.alice
    bob = marketaccounts.bob
    pyopentxs.otme.create_market_offer(bob.account1._id, bob.account2._id,
                                       1, 1, 3, 7, False, 10000, "", 0)

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
    pyopentxs.otme.create_market_offer(bob.account1._id, bob.account2._id,
                                       1, 1, 3, 7, True, 10000, "", 0)

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
