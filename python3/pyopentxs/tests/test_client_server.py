import pytest
from pyopentxs import (server, ReturnValueError, is_message_success, error, instrument)
from pyopentxs.nym import Nym
from pyopentxs.asset import Asset
from pyopentxs import account
from datetime import datetime, timedelta
from pyopentxs.instrument import transfer, write

# def test_check_server_id():
#     nym_id = pyopentxs.create_nym()
#     assert pyopentxs.check_server_id(get_server_id(), nym_id)

btc_contract_file = "../test-data/sample-contracts/btc.xml"


def test_register_nym():
    Nym().register(server_id=server.first_id())


def test_issue_asset_contract():
    server_id = server.first_id()
    nym = Nym().register(server_id)
    Asset().issue(nym, open(btc_contract_file), server_id)


def test_create_account():
    server_id = server.first_id()
    nym = Nym().register(server_id)
    asset = Asset().issue(nym, open(btc_contract_file), server_id)
    myacct = account.Account(asset, nym).create()

    accounts = account.get_all_ids()
    assert myacct._id in accounts


class TransferAccounts:
    '''A class to hold issuer/source/target accounts to test transfers.
       Start with 100 balance in the source account'''
    def __init__(self):
        server_id = server.first_id()

        self.asset = Asset().issue(Nym().register(server_id),
                                   open(btc_contract_file), server_id)

        self.source = account.Account(self.asset, Nym().register(server_id)).create()
        self.target = account.Account(self.asset, Nym().register(server_id)).create()
        self.issuer = self.asset.issuer_account

    def initial_balance(self, balance=100):
        # send 100 from issuer to nym_source_id
        # self.cheque = new_cheque(self.issuer, self.source, balance)
        # transfer(self.cheque, self.issuer, self.source)
        transfer(balance, self.issuer, self.source)
        return self

    def assert_balances(self, issuer, source, target):
        assert (issuer, source, target) == (self.issuer.balance(),
                                            self.source.balance(),
                                            self.target.balance()),\
            "Issuer/source/target balances do not match."


def new_cheque(source, target, amount, valid_from=-10000, valid_to=10000, source_nym=None):
    now = datetime.utcnow()
    return instrument.Cheque(
        source.server_id,
        amount,
        now + timedelta(0, valid_from),
        now + timedelta(0, valid_to),
        source,
        source_nym or source.nym,
        "test cheque!",
        target.nym
    )


def new_voucher(source, target, amount, source_nym=None):
    return instrument.Voucher(
        source.server_id, amount, source, source_nym or source.nym, "test cheque!", target.nym)


def new_transfer(source, target, amount):
    return amount


@pytest.fixture()
def prepared_accounts(request):
    accts = TransferAccounts()
    accts.initial_balance()
    return accts


class TestGenericTransfer:
    def pytest_generate_tests(self, metafunc):
        transfer_amount_data = [
            (-10, False),
            (10, True),
            (200, False),
            (0, False)
        ]
        instrument_data = [new_cheque,
                           new_voucher,
                           new_transfer]
        metafunc.parametrize("amount,should_pass", argvalues=transfer_amount_data)
        metafunc.parametrize("instrument_constructor", argvalues=instrument_data)

    def test_simple_transfer(self, prepared_accounts, amount, should_pass, instrument_constructor):
        instrument = instrument_constructor(
            prepared_accounts.source, prepared_accounts.target, amount)
        with error.expected(None if should_pass else ReturnValueError):
            transfer(instrument, prepared_accounts.source, prepared_accounts.target)
        if should_pass:
            prepared_accounts.assert_balances(-100, 100 - amount, amount)
        else:
            prepared_accounts.assert_balances(-100, 100, 0)


@pytest.mark.parametrize("instrument_constructor", [new_cheque, new_voucher])
def test_not_account_owner(prepared_accounts, instrument_constructor):
    '''Test that we get a graceful failure when we try to deposit an
       instrument for an account we don't own'''

    instrument = instrument_constructor(
        prepared_accounts.source, prepared_accounts.target, 50,
        source_nym=prepared_accounts.target.nym)
    with error.expected(ReturnValueError):
        transfer(instrument, prepared_accounts.source, prepared_accounts.target)


@pytest.mark.parametrize("instrument_constructor",
                         [new_cheque,

                          pytest.mark.skipif(
                              True,
                              reason="https://github.com/Open-Transactions/opentxs/issues/324")
                          ((new_voucher,)),

                          new_transfer])
def test_wrong_asset_type(instrument_constructor):
    '''Try to transfer eg a cheque from one asset account to another of a
       different type. Should fail'''
    ta_asset1 = TransferAccounts().initial_balance()
    ta_asset2 = TransferAccounts().initial_balance()
    source = ta_asset1.source
    target = ta_asset2.target
    instrument = instrument_constructor(source, target, 50)
    with error.expected(ReturnValueError):
        transfer(instrument, source, target)
    ta_asset2.assert_balances(-100, 100, 0)


@pytest.mark.parametrize("instrument_constructor",
                         [
                             new_cheque,
                             # new_voucher (not found in outbox?)
                         ])
def test_cancel_instrument(instrument_constructor):
    '''Cancel an instrument and make sure it can't be deposited.'''
    accounts = TransferAccounts().initial_balance()
    instrument = instrument_constructor(accounts.source, accounts.target, 50)
    write(instrument)
    instrument.cancel()
    with error.expected(ReturnValueError):
        instrument.deposit(accounts.target.nym, accounts.target)
    accounts.assert_balances(-100, 100, 0)


class TestChequeTransfer:
    @pytest.mark.parametrize("amount,first_valid,later_income,second_valid", [
        # not enough funds
        (200, False, 100, True),
        (200, False, 50, False),
        # cheque can be used only once
        (10, True, 0, False),
        (10, True, 1, False),
    ])
    def test_deposit_twice(self, prepared_accounts, amount, first_valid, later_income,
                           second_valid):
        # create cheque and try to deposit it
        cheque = new_cheque(prepared_accounts.source, prepared_accounts.target, amount)
        with error.expected(None if first_valid else ReturnValueError):
            transfer(cheque, prepared_accounts.source, prepared_accounts.target)

        expected_source = 100
        expected_target = 0
        if (first_valid):
            expected_source -= amount
            expected_target += amount
        prepared_accounts.assert_balances(-100, expected_source, expected_target)

        # now transfer more funds to source
        if later_income != 0:
            income = new_cheque(prepared_accounts.issuer, prepared_accounts.source, later_income)
            transfer(income, prepared_accounts.issuer, prepared_accounts.source)
        expected_source += later_income

        # and repeat cheque deposit
        with error.expected(None if second_valid else ReturnValueError):
            deposit = cheque.deposit(prepared_accounts.target.nym, prepared_accounts.target)
        if second_valid:
            expected_source -= amount
            expected_target += amount
            assert is_message_success(deposit)

        prepared_accounts.assert_balances(-100 - later_income, expected_source, expected_target)

    @pytest.mark.parametrize("valid_from,valid_to,valid", [
        # valid cheque
        (-100, 100, True),
        # cheque is expired
        (-100, -50, False),
        # not yet valid
        (500, 100, False),
        # incorrect intervals
        (-100, -200, False),
        (100, -100, False),
        (200, 100, False),
    ])
    def test_expired_cheque(self, prepared_accounts, valid_from, valid_to, valid):
        with error.expected(None if valid else ReturnValueError):
            transfer(new_cheque(prepared_accounts.source, prepared_accounts.target, 10,
                                valid_from, valid_to),
                     prepared_accounts.source,
                     prepared_accounts.target)
        if valid:
            prepared_accounts.assert_balances(-100, 90, 10)
        else:
            prepared_accounts.assert_balances(-100, 100, 0)
