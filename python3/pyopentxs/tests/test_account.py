from pyopentxs.nym import Nym
from pyopentxs.asset import Asset
from pyopentxs import account, error, ReturnValueError
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


def test_account_nym_not_registered():
    nym = Nym().register()
    asset = Asset().issue(nym, open(data.btc_contract_file))
    with error.expected(ReturnValueError):
        account.Account(asset, Nym().create()).create()


def test_asset_nym_not_registered():
    with error.expected(ReturnValueError):
        Asset().issue(Nym().create(), open(data.btc_contract_file))


@pytest.mark.skipif(True, reason="https://github.com/Open-Transactions/opentxs/issues/364")
def test_delete_account(an_account):
    an_account.create()
    an_account.delete()
