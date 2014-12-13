from pyopentxs.tests import data
import pyopentxs
import pytest
import time

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
