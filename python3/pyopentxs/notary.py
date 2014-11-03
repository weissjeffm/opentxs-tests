import pyopentxs
import opentxs
from pyopentxs import nym, config_dir, decode, server
from contextlib import closing
from bs4 import BeautifulSoup
import io
import os
import shutil


def setup(contract_stream):
    '''
    Helps create a clean config dir starting from scratch.
    '''
    pyopentxs.init()
    server_nym = nym.Nym().create()
    with closing(contract_stream):
        server_contract = server.add(server_nym._id, contract_stream.read())
    walletxml = decode(open(config_dir + "client_data/wallet.xml"))
    cached_key = BeautifulSoup(walletxml).wallet.cachedkey.string.strip()
    signed_contract_file = config_dir + "client_data/contracts/" + server_contract
    with closing(open(signed_contract_file)) as f:
        signed_contract = f.read()
    decoded_signed_contract = decode(io.StringIO(signed_contract))

    # copy the credentials to the server
    server_data_dir = config_dir + "server_data/"
    if not os.path.exists(server_data_dir):
        os.mkdir(server_data_dir)
    shutil.copytree(config_dir + "client_data/credentials", server_data_dir + "credentials")
    # remove the client-side data
    shutil.rmtree(config_dir + "client_data")

    # reread the client data (empty)
    pyopentxs.init()

    # since we still don't have programmatic access, just print the info
    # for easy copying
    print(server_contract)
    print(server_nym._id)
    print(cached_key + "\n~")
    print("\n~")
    print(decoded_signed_contract + "\n~")

    # next line crashes the process
    # opentxs.MainFile(None).CreateMainFile(signed_contract, server_contract, "", server_nym,
    # cached_key)
    # add the server contract on the client side
    opentxs.OTAPI_Wrap_AddServerContract(decoded_signed_contract)

    return decoded_signed_contract
