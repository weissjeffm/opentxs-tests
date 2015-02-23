from pyopentxs import ReturnValueError
from pyopentxs.nym import Nym
import opentxs

from bs4 import BeautifulSoup
from pyopentxs import otme


class Account:
    def __init__(self, asset=None, nym=None, server_id=None, name=None, _id=None):
        self.server_id = server_id or (asset and asset.server_id)
        self.nym = nym or Nym().register()
        self.asset = asset
        self._id = _id
        self.name = name

    def create(self):
        if self._id:
            raise ValueError("Can't create the same account twice,\
            to create an account of the same type, create a new Account object first.")
        account_xml = otme.create_asset_acct(self.server_id, self.nym._id, self.asset._id)
        s = BeautifulSoup(account_xml)
        # new message name
        if s.registeraccountresponse:
            self._id = s.registeraccountresponse['accountid']

        # todo: old message name, remove in due time.
        elif s.createaccountresponse:
            self._id = s.createaccountresponse['accountid']

        else:
            raise ReturnValueError("No account id present in response, account not created.")

        # set the name if any
        if self.name:
            opentxs.OTAPI_Wrap_SetAccountWallet_Name(self._id, self.nym._id, self.name)
        return self

    def delete(self):
        deleted = opentxs.OTAPI_Wrap_deleteAssetAccount(self.server_id, self.nym._id, self._id)
        # print("deleting {} returned {}".format(self._id, deleted))
        assert deleted > 0, "Unable to delete account {}, return code {}".format(self._id, deleted)

    def balance(self):
        """
        refresh local account files from server and return account balance
        """
        assert self._id, "Account must be created first."

        if hasattr(opentxs, 'OTAPI_Wrap_getAccountData'):  # new api name
            res = opentxs.OTAPI_Wrap_getAccountData(self.server_id, self.nym._id, self._id)
        else:  # todo: old api name, remove in due time
            res = opentxs.OTAPI_Wrap_getAccountFiles(self.server_id, self.nym._id, self._id)
        if res < 0:
            raise ReturnValueError(res)
        return opentxs.OTAPI_Wrap_GetAccountWallet_Balance(self._id)

    def accept_payments(self, indices=None):
        otme.retrieve_nym(self.server_id, self.nym._id)
        if not indices:
            # build a list of indices
            ledger = opentxs.OTAPI_Wrap_LoadPaymentInbox(self.server_id, self.nym._id)
            payment_count = opentxs.OTAPI_Wrap_Ledger_GetCount(self.server_id, self.nym._id,
                                                           self._id, ledger)
            indices = list(map(str, range(payment_count)))
        otme.accept_from_paymentbox(self._id, ",".join(indices), "")

    def __repr__(self):
        return "<Account id={}, asset={}, nym={}, server_id={}>".format(
            self._id, self.asset, self.nym, self.server_id)


def get_all_ids():
    account_count = opentxs.OTAPI_Wrap_GetAccountCount()
    accounts = []
    for i in range(account_count):
        _id = opentxs.OTAPI_Wrap_GetAccountWallet_ID(i)
        accounts.append(_id)

    return accounts
