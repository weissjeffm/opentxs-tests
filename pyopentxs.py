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


def create_pseudonym(keybits=1024, nym_id_source="", alt_location=""):
    """
    Create a new pseudonym.

    Returns pseudonym id?
    """
    retval = _otme.create_pseudonym(keybits, nym_id_source, alt_location)

    if retval == '':
        raise ReturnValueError(retval)

    return retval


def check_user(server, nym, target_nym):
    # TODO
    # see ot wiki "API" / "Write a checkque"
    return _otme.check_user(server, nym, target_nym)


def get_nym_ids():
    """
    return list of registered nym ids
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


def get_nym_name(nym_id):
    """
    Get the nym name for a given id
    """

    # FIXME: test and fix crash for empty nym_id
    # FIXME: discern between "empty name" and "nym not found"
    retval = opentxs.OTAPI_Wrap_GetNym_Name(nym_id)

    if retval == '':
        raise ReturnValueError(retval)

    return retval





def test_register_nym():
    pass


def exit_handler():
    opentxs.OTAPI_Wrap_AppCleanup()


if __name__ == "__main__":
    #get_nym_name("")
    pass
