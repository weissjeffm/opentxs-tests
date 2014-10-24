import opentxs
import pyopentxs
from pyopentxs import nym, config_dir, decode
from contextlib import closing
from bs4 import BeautifulSoup
import io
import os
import shutil


def add(nym_id, contract):
    '''Create a server contract with the given nym_id and the contract
    contents.'''
    contract_id = opentxs.OTAPI_Wrap_CreateServerContract(nym_id, contract)
    assert(len(contract_id) > 0)
    return contract_id


def setup(contract_stream):
    '''
    Helps create a clean config dir starting from scratch.
    '''
    pyopentxs.init()
    server_nym = nym.Nym().create()
    with closing(contract_stream):
        server_contract = add(server_nym._id, contract_stream.read())
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

    # since we still don't have programmatic access, just print the info
    # for easy copying
    print(server_contract)
    print(server_nym._id)
    print(cached_key + "\n~")
    print(decoded_signed_contract + "\n~")

    # next line crashes the process
    # opentxs.MainFile(None).CreateMainFile(signed_contract, server_contract, "", server_nym,
    # cached_key)
    # add the server contract on the client side
    opentxs.OTAPI_Wrap_AddServerContract(decoded_signed_contract)

    return decoded_signed_contract


def get_all():
    '''Return a list of pairs of [id, name] of all the locally registered servers.'''
    server_count = opentxs.OTAPI_Wrap_GetServerCount()
    servers = []
    for i in range(server_count):
        server_id = opentxs.OTAPI_Wrap_GetServer_ID(i)
        server_name = opentxs.OTAPI_Wrap_GetServer_Name(server_id)
        servers.append([server_id, server_name])

    return servers


def first_id():
    return get_all()[0][0]


def check_id(server_id, user_id):
    """
    Returns true if the server is available and the user (same as nym) exists.
    """

    # The user_id parameters here is the same as nym_id in other api calls

    # The method is described as a "ping" in the API documentation, which should
    # be called after wallet initialized. However a remote account on the server
    # is required.

    retval = opentxs.OTAPI_Wrap_checkServerID(server_id, user_id)

    print("(debug) check_server_id retval=", retval)

    # The return value `1` for success is defined by
    #     case (OTClient::checkServerId)
    # in OTClient::ProcessUserCommand()

    return retval == 1
