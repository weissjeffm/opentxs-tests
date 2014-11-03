from pyopentxs import account
from pyopentxs.nym import Nym
from pyopentxs.asset import Asset
from pyopentxs.instrument import transfer
btc_contract_file = "../test-data/sample-contracts/btc.xml"


class TransferAccounts:
    '''A class to hold issuer/source/target accounts to test transfers.
       Start with 100 balance in the source account'''
    def __init__(self):
        self.asset = Asset().issue(Nym().register(),
                                   open(btc_contract_file))

        self.source = account.Account(self.asset, Nym().register()).create()
        self.target = account.Account(self.asset, Nym().register()).create()
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
