import pyopentxs
from datetime import datetime, timedelta

# def test_check_server_id():
#     nym_id = pyopentxs.create_nym()
#     assert pyopentxs.check_server_id(get_server_id(), nym_id)

btc_contract_file = "../test-data/sample-contracts/btc.xml"


def register_new_nym():
    nym_id = pyopentxs.create_nym()
    pyopentxs.register_nym(pyopentxs.first_server_id(), nym_id)
    return nym_id


def test_register_nym():
    register_new_nym()


def test_issue_asset_contract():
    nym_id = register_new_nym()
    server_id = pyopentxs.first_server_id()
    pyopentxs.issue_asset_type(server_id, nym_id, open(btc_contract_file))


def test_issue_write_cheque():
    server_id = pyopentxs.first_server_id()

    nym_target_id = register_new_nym()

    nym_id = register_new_nym()
    asset = pyopentxs.issue_asset_type(server_id, nym_id, open(btc_contract_file))

    account_id = pyopentxs.create_account(server_id, nym_id, asset.asset_id)
    target_account_id = pyopentxs.create_account(server_id, nym_target_id, asset.asset_id)

    now = datetime.now()
    cheque = pyopentxs.Cheque(server_id, 10, now + timedelta(0, -1), now + timedelta(0, 1000),
                              asset.issuer_account_id, nym_id, "memo", nym_target_id)

    cheque.write()
    deposit = cheque.deposit(nym_target_id, target_account_id)
    assert pyopentxs.is_message_success(deposit)

def test_create_account():
    server_id = pyopentxs.first_server_id()
    nym_id = register_new_nym()
    asset = pyopentxs.issue_asset_type(server_id, nym_id, open(btc_contract_file))
    account_id = pyopentxs.create_account(server_id, nym_id, asset.asset_id)

    accounts = pyopentxs.get_account_ids()

    assert account_id in accounts
