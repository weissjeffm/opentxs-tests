from pyopentxs import server, nym
import pytest

pytest.mark.usefixtures("setup_ot_config")


def test_create_nym():
    nym_id = nym.Nym().create()._id
    nym_ids = [n._id for n in nym.get_all()]

    assert (nym_id in nym_ids), "nym_id=%r" % nym_id


def test_list_servers():
    servers = server.get_all()
    assert servers != []
    assert servers[0][1] == "Transactions.com"  # from localhost.xml server contract
