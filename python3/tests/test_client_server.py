import pyopentxs
import pytest
# def test_check_server_id():
#     nym_id = pyopentxs.create_nym()
#     assert pyopentxs.check_server_id(get_server_id(), nym_id)


def register_new_nym():
    nym_id = pyopentxs.create_nym()
    pyopentxs.register_nym(pyopentxs.first_server_id(), nym_id)
    return nym_id


def test_register_nym():
    register_new_nym()


def test_issue_asset_contract():
    nym_id = register_new_nym()
    server_id = pyopentxs.first_server_id()
    pyopentxs.issue_asset_type(server_id, nym_id, open("../test-data/sample-contracts/btc.xml"))


def foo_test_create_account():
    server_id = pyopentxs.first_server_id()

    nym_id = register_new_nym()

    assets = pyopentxs.get_assets()
    asset_id = assets[0][0]

    account_id = pyopentxs.create_account(server_id, nym_id, asset_id)

    accounts = pyopentxs.get_account_ids()

    assert account_id in accounts
