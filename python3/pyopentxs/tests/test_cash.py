from pyopentxs import cash, error, ReturnValueError
from pyopentxs.instrument import Cash
import pytest


@pytest.mark.parametrize("amount", [10, 100, 0, -1, 101])
def test_out_of_band(prepared_accounts, amount):
    '''Export cash, pass it to other nym, he deposits it'''
    source = prepared_accounts.source
    target = prepared_accounts.target
    cash.create_mint(prepared_accounts.asset)
    c = Cash(amount)
    shoulderror = lambda amount: amount <= 0 or amount > 100
    with error.expected(ReturnValueError if shoulderror(amount) else None):
        c.export(source, nym=target.nym)
    if not shoulderror(amount):
        c.deposit(target)
        prepared_accounts.assert_balances(-100, 100 - amount, amount)
    else:
        prepared_accounts.assert_balances(-100, 100, 0)


def test_deposit_wrong_nym(prepared_accounts):
    '''Export cash to one nym, try to deposit with another - should fail'''
    source = prepared_accounts.source
    target = prepared_accounts.target
    issuer = prepared_accounts.issuer

    cash.create_mint(prepared_accounts.asset)
    c = Cash(10)
    c.export(source, nym=issuer.nym)  # export to the issuer but
    with error.expected(ReturnValueError):
        c.deposit(target)  # try to deposit as the target
    # the cash is still taken out of the account
    prepared_accounts.assert_balances(-100, 90, 0)


def test_lost_cash(prepared_accounts):
    '''Use the backup purse (for sender) to use in case the recipient loses his'''
    source = prepared_accounts.source
    target = prepared_accounts.target

    cash.create_mint(prepared_accounts.asset)
    c = Cash(10)
    c.export(source, nym=target.nym)  # export to the target but
    # deposit using the backup purse into the source's account
    c.deposit(source, nym=source.nym, purse=c.backup_purse)
    # cash ends up back where it started, in source account
    prepared_accounts.assert_balances(-100, 100, 0)
