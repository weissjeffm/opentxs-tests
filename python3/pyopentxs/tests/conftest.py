import pyopentxs
import pytest


@pytest.fixture(scope="session", autouse=True)
def initialize_pyopentxs():
    ''' Initialize the client. If called from the runtests.py wrapper script,
    this will have already been called (along with cleaning the ot config dir)
    but calling it again appears to be harmless.

    '''
    pyopentxs.init()
