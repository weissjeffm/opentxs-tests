import os
import atexit

"""
This file is a small abstraction layer for the SWIG-generated python API
and does the required initialization on import.

The goal also is to capture errors gracefully.
"""

import opentxs


class ReturnValueError(BaseException):
    """
    The return value of an API function has signaled an error condition
    """
    def __init__(self, return_value):
        self.return_value = return_value

    def __str__(self):
        return "API function has returned error value %r" % self.return_value



class ProcessUserCommand:
    """
    These return values are used by ProcessUserCommand() and bubble up
    to different higher-level APIs. The return value is documented in
    OTClient::ProcessUserCommand()
    """

    # error, don't send message
    Error = 0               # error, don't send message

    # no error, no message sent
    NoMessageSent = -1

    # Paraphrasing the documentation
    # message is sent, no request number returns > 0 for
    # processInbox, containing the number that was there
    # before processing -- FIXME unclear
    MessageSent = 1

    # This is sometimes returned by  OTClient::CalcReturnVal()
    # Low-level networking error
    RequestNumberMismatch = -2



def _remove_pid():
    """
    Remove the PID file if one exists
    """

    # There should not be a long-running opentxs client running anyway.
    # An existing PID file probably indicates a crashed process, not a running
    # instance
    pid_file = os.path.expanduser("~/.ot/client_data/ot.pid")
    if os.path.exists(pid_file):
        print("removing lockfile %s" % pid_file)
        os.remove(pid_file)



def _init_txs():
    """
    Initialize the OTAPI in order to get a working state
    """
    # This should only be done once per process.
    opentxs.OTAPI_Wrap_AppInit()
    opentxs.OTAPI_Wrap_LoadWallet()


_remove_pid()

_init_txs()

# OTME = OpenTransactions MadeEasy
_otme = opentxs.OT_ME()


### API methods that DONT include server communication

def create_pseudonym(keybits=1024, nym_id_source="", alt_location=""):
    """
    Create a new pseudonym in the local wallet.

    Crashes with OT_FAIL if keysize is invalid.

    Returns generated pseudonym id.
    """
    retval = _otme.create_pseudonym(keybits, nym_id_source, alt_location)

    if retval == '':
        # the pseudonym id should be a 43-byte hash
        raise ReturnValueError(retval)

    return retval


def check_user(server, nym, target_nym):
    # TODO
    # see ot wiki "API" / "Write a checkque"
    return _otme.check_user(server, nym, target_nym)



### Wallet operations
#
# These methods (probably) return the data stored in the local wallet
#

def get_nym_ids():
    """
    Return list of locally stored nyms.
    """
    nym_count = opentxs.OTAPI_Wrap_GetNymCount()
    nym_ids = []
    for i in range(nym_count):
        retval = opentxs.OTAPI_Wrap_GetNym_ID(i)
        if retval == '':
            # this is just a guess, a nym_id should never be an empty string
            raise ReturnValueError(retval)
        nym_ids.append(retval)

    return nym_ids


def get_assets():
    """
    Returns an array of assets described as tuples (id, name)
    """
    asset_count = opentxs.OTAPI_Wrap_GetAssetTypeCount()
    assets = []
    for i in range(asset_count):
        asset_id = opentxs.OTAPI_Wrap_GetAssetType_ID(i)
        asset_name = opentxs.OTAPI_Wrap_GetAssetType_Name(asset_id)
        assets.append((asset_id, asset_name))

    return assets


def get_nym_name(nym_id):
    """
    Return the nym name for a given id.

    Attention: If the nym for the id cannot be found, an empty string is
    returned.
    """

    # FIXME: test and fix crash for empty nym_id
    # FIXME: discern between "empty name" and "nym not found"
    retval = opentxs.OTAPI_Wrap_GetNym_Name(nym_id)

    if retval == '':
        raise ReturnValueError(retval)

    return retval




### API methods that include server communication

def check_server_id(server_id, user_id):
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


def register_nym(server_id, nym_id):
    """
    Register nym on server.

    Returns the response message from the server.
    """
    # TODO: what is the response message?
    retval = _otme.register_nym(server_id, nym_id)

    if retval == '':
        raise ReturnValueError(retval)

    return retval

### cleanup methods

def exit_handler():
    opentxs.OTAPI_Wrap_AppCleanup()


### api utils

def _dump_api_methods():
    for attribute in dir(opentxs):
        print(attribute)

if __name__ == "__main__":
    import sys

    if '--dump-api' in sys.argv:
        _dump_api_methods()

