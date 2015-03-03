import pyopentxs
import opentxs
from pyopentxs import nym, client_config_dir, notary_config_dir, decode, server
from contextlib import closing
from bs4 import BeautifulSoup
import io
import os
import shutil
import psutil
import configparser


def make_server_contract(contract, server_nym):
    '''Takes a stream for a template contract, returns a tuple of
       (contract, cached_key, decoded_signed_contract)'''
    server_contract = server.add(server_nym._id, contract)
    walletxml = decode(open(client_config_dir + "client_data/wallet.xml"))
    cached_key = BeautifulSoup(walletxml).wallet.cachedkey.string.strip()
    signed_contract_file = client_config_dir + "client_data/contracts/" + server_contract
    with closing(open(signed_contract_file)) as f:
        signed_contract = f.read()
    decoded_signed_contract = decode(io.StringIO(signed_contract))
    return (server_contract, cached_key, decoded_signed_contract)


def setup(contract_stream, total_servers=1):
    '''
    Helps create a clean config dir starting from scratch.
    contract_stream is an input stream pointing to a template contract file.
    total_servers is an integer, of how many servers the client should have on file.
    Only the first server will actually exist, the rest will appear as offline.
    '''
    pyopentxs.init()
    server_nym = nym.Nym().create()

    contract = contract_stream.read()
    contract_stream.close()

    server_contract_id, cached_key, decoded_signed_contract \
        = make_server_contract(contract, server_nym)

    walletxml = decode(open(client_config_dir + "client_data/wallet.xml"))
    cached_key = BeautifulSoup(walletxml).wallet.cachedkey.string.strip()
    signed_contract_file = client_config_dir + "client_data/contracts/" + server_contract_id
    with closing(open(signed_contract_file)) as f:
        signed_contract = f.read()
    decoded_signed_contract = decode(io.StringIO(signed_contract))

    # copy the credentials to the server
    server_data_dir = notary_config_dir + "server_data/"
    if not os.path.exists(server_data_dir):
        os.mkdir(server_data_dir)
    shutil.copytree(client_config_dir + "client_data/credentials", server_data_dir + "credentials")
    # remove the client-side data
    shutil.rmtree(client_config_dir + "client_data")

    # reread the client data (empty)
    pyopentxs.init()
    print("reread client data")
    # since we still don't have programmatic access, just write the info
    # to use later to pipe to the notary process
    output = io.BytesIO()
    writeit = lambda s: output.write(s.encode("utf-8"))
    writeit(server_contract_id + "\n")
    writeit(server_nym._id + "\n")
    writeit(cached_key + "\n~\n~\n")
    writeit(decoded_signed_contract + "\n~\n")

    # the following crashes the process, so we pipe the info manually
    # opentxs.MainFile(None).CreateMainFile(signed_contract, server_contract_id, "", server_nym,
    # cached_key)

    # add the server contract on the client side
    opentxs.OTAPI_Wrap_AddServerContract(decoded_signed_contract)

    # should be just one known active server now
    server.active = [server_contract_id]

    # create any extra fake servers
    for _ in range(total_servers - 1):
        opentxs.OTAPI_Wrap_AddServerContract(
            make_server_contract(contract, nym.Nym().create())[2])

    return output


def restart():
    # pyopentxs.cleanup()
    print("cleaned up")
    # kill existing processes
    for proc in psutil.process_iter():
        if proc.name() == "opentxs-notary":
            proc.kill()
            psutil.wait_procs([proc], timeout=10)
    print("killed old notaries")
    # start new
    os.system("opentxs-notary > opentxs-notary.log 2>&1 &")
    print("Started notary process")

    # start
    pyopentxs.init()


class Config:
    def __init__(self, filename=None):
        self.filename = filename or notary_config_dir + "server.cfg"

    def read(self):
        '''Retrieves the server config file and parses it'''
        self.parser = configparser.ConfigParser()
        self.parser.read(notary_config_dir + "server.cfg")
        return self.parser

    def write(self):
        f = open(self.filename, 'w')
        self.parser.write(f)
        f.close()

config = Config()
