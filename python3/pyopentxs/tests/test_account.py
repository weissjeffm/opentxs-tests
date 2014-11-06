from pyopentxs.nym import Nym
from pyopentxs.asset import Asset
from pyopentxs import account
from pyopentxs.tests import data
import pytest


@pytest.fixture(scope='function')
def an_account():
    '''Generates a test account'''
    nym = Nym().register()
    asset = Asset().issue(nym, open(data.btc_contract_file))
    return account.Account(asset, nym).create()


def test_create_account(an_account):
    an_account.create()
    accounts = account.get_all_ids()
    assert an_account._id in accounts


@pytest.mark.skipif(True, reason="https://github.com/Open-Transactions/opentxs/issues/364")
def test_delete_account(an_account):
    an_account.create()
    an_account.delete()
