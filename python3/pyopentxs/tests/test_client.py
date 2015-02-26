from pyopentxs import server, nym, asset
import pytest
import opentxs
import time
from bs4 import BeautifulSoup
import io
from pyopentxs.tests import data

pytest.mark.usefixtures("setup_ot_config")


def test_create_nym():
    nym_id = nym.Nym().create()._id
    nym_ids = [n._id for n in nym.get_all()]

    assert (nym_id in nym_ids), "nym_id=%r" % nym_id


def test_list_servers():
    servers = server.get_all()
    assert servers != []
    assert servers[0][1] == "Transactions.com"  # from localhost.xml server contract


def make_contract(basefile, replacements):
    '''Returns a stream for an asset contract, with the currency attribute
       values replaced with the given arguments.'''
    f = open(basefile)
    contract = f.read()
    xmldata = BeautifulSoup(contract)
    for (attr, val) in replacements.items():
        xmldata.currency[attr] = val
    return io.StringIO(str(xmldata))


@pytest.mark.parametrize(
    "attrs,number,expected_formatted",
    [
        [{'factor': '1000000', 'decimal_power': '6'}, 123456789, "BTC 123.456789"],
        [{'factor': '100', 'decimal_power': '2', 'symbol': "$"}, 123456789, "$ 1,234,567.89"],
        [{'factor': '16', 'decimal_power': '2', 'symbol': "£"}, 49, "£ 3.01"],
        [{'factor': '100', 'decimal_power': '2'}, 0, "BTC 0.00"],
        [{'factor': '1', 'decimal_power': '2'}, 0, "BTC 0"],
        [{'factor': '1', 'decimal_power': '2'}, 10000, "BTC 10,000"],
        # [{'factor': '1', 'decimal_power': '2'}, -1, "BTC -1"], # fails "-BTC 1"
    ])
def test_format_amount(attrs, number, expected_formatted):
    contract_stream = make_contract("../test-data/sample-contracts/btc.xml", attrs)
    myasset = asset.Asset().issue(nym.Nym().register(), contract_stream)
    actual_formatted = opentxs.OTAPI_Wrap_FormatAmount(myasset._id, number)
    assert actual_formatted == expected_formatted


def test_get_time():
    '''Verify opentxs client time and python's time are the same'''
    assert abs(opentxs.OTAPI_Wrap_GetTime() - time.time()) < 1
