import pyopentxs

# def test_check_server_id():
#     nym_id = pyopentxs.create_pseudonym()
#     assert pyopentxs.check_server_id(get_server_id(), nym_id)


def test_register_nym():
    nym_id = pyopentxs.create_pseudonym()
    pyopentxs.register_nym(pyopentxs.first_server_id(), nym_id)


def test_create_asset():
    pass


def test_create_account():
    server_id = pyopentxs.first_server_id()

    nym_id = pyopentxs.create_pseudonym()
    pyopentxs.register_nym(server_id, nym_id)

    assets = pyopentxs.get_assets()
    asset_id = assets[0][0]

    account_id = pyopentxs.create_account(server_id, nym_id, asset_id)

    accounts = pyopentxs.get_account_ids()

    assert account_id in accounts
