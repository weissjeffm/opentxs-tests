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
