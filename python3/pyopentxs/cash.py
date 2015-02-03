import subprocess
from pyopentxs import server  # , ReturnValueError, instrument
# import opentxs


def create_mint(asset):
    '''Creates the mint (via createmint command line tool) for the given
       asset'''
    server_nym_id = server.nym_id(asset.server_id)
    output = subprocess.call(["createmint", asset.server_id, server_nym_id, asset._id])
    # time.sleep(2)
    return output


# def import_purse(purse, asset, owner_nym):
#     imported = opentxs.OTAPI_Wrap_Wallet_ImportPurse(
#         asset.server_id, asset._id, owner_nym._id, purse)
#     if not imported:
#         raise ReturnValueError("Unable to import purse for asset: {}".format(asset))
#     return instrument.Cash()
