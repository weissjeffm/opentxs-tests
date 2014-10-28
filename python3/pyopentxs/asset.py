import opentxs
from pyopentxs import is_message_success, otme
from pyopentxs.account import Account


class Asset:
    def __init__(self, server_id=None, _id=None):
        self.server_id = server_id
        self._id = _id

    def create_contract(self, nym, contract_stream):
        asset_id = opentxs.OTAPI_Wrap_CreateAssetContract(nym._id, contract_stream.read())
        assert asset_id
        self.issuer = nym
        self._id = asset_id

    def issue(self, nym=None, contract_stream=None, server_id=None, issue_for_nym=None):
        '''Issues a new asset type on the given server and nym.  contract
           should be a string with the contract contents.

           nym must be registered.

           issue_for_nym is the nym to try to create the issuer account as (OT shouldn't allow
             if this isn't the same as the issuer nym) - for testing purposes
        '''
        # first create the contract if necessary
        self.server_id = self.server_id or server_id
        assert self.server_id
        if not self._id:
            self.create_contract(nym, contract_stream)
        signed_contract = opentxs.OTAPI_Wrap_GetAssetType_Contract(self._id)
        message = otme.issue_asset_type(server_id, (issue_for_nym and issue_for_nym._id) or nym._id,
                                        signed_contract)
        assert is_message_success(message)
        account_id = opentxs.OTAPI_Wrap_Message_GetNewIssuerAcctID(message)
        self.issuer_account = Account(asset=self, nym=self.issuer, server_id=self.server_id,
                                      _id=account_id)
        return self

    def __repr__(self):
        return "<Asset id={}, issuer={}, server_id={}>".format(
            self._id, self.issuer, self.server_id)


def get_all():
    """
    Returns an array of assets described as tuples(id, name)
    """
    asset_count = opentxs.OTAPI_Wrap_GetAssetTypeCount()
    assets = []
    for i in range(asset_count):
        asset_id = opentxs.OTAPI_Wrap_GetAssetType_ID(i)
        asset_name = opentxs.OTAPI_Wrap_GetAssetType_Name(asset_id)
        assets.append([asset_id, asset_name])

    return assets
