import pyopentxs

# this is defined by the sample data
SERVER_ID = "r1fUoHwJOWCuK3WBAAySjmKYqsG6G2TYIxdqY6YNuuG"


def test_check_server_id():
    nym_id = pyopentxs.create_pseudonym()
    assert pyopentxs.check_server_id(SERVER_ID, nym_id)

def test_register_nym():
    nym_id = pyopentxs.create_pseudonym()
    pyopentxs.register_nym(SERVER_ID, nym_id)
    # returns server "contract"
    # TODO: maybe perform checks on the returned contract


def test_create_account():
    servers = pyopentxs.get_servers()
    server_id = servers[0][0]

    nym_id = pyopentxs.create_pseudonym()
    pyopentxs.register_nym(server_id, nym_id)

    assets = pyopentxs.get_assets()
    asset_id = assets[0][0]

    account_id = pyopentxs.create_account(server_id, nym_id, asset_id)

    accounts = pyopentxs.get_account_ids()

    assert account_id in accounts
