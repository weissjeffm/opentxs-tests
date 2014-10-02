import pyopentxs
import shutil
import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_ot_config():
    '''Replace the OT config dir with clean data, containing only a server
       contract and client/server wallets.  Initialize the client.

    '''
    # copy the clean data directory
    print("hello!!!")
    shutil.rmtree(pyopentxs.config_dir)
    shutil.copytree("../ot-clean-data/.ot", pyopentxs.config_dir)
    pyopentxs.init()
