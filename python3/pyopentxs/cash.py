import subprocess
from pyopentxs import server
# import opentxs


def create_mint(asset):
    '''Creates the mint (via createmint command line tool) for the given
       asset'''
    server_nym_id = server.nym_id(asset.server_id)
    output = subprocess.call(["createmint", asset.server_id, server_nym_id, asset._id])
    # time.sleep(2)
    return output
