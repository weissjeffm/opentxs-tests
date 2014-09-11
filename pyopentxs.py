import os

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


def create_pseudonym(keybits, nym_id_source, alt_location):
    """
    Create a new pseudonym.

    Returns pseudonym id?
    """
    retval = _otme.create_pseudonym(keybits, nym_id_source, alt_location)

    if retval == '':
        raise ReturnValueError(retval)

    return retval

def verify_message():
    pass

def check_user(server, nym, target_nym):
    # see ot wiki "API" / "Write a checkque"
    return _otme.check_user(server, nym, target_nym)



if __name__ == "__main__":
    retval = create_pseudonym(2 ** 12, "", "")
    print(repr(retval), len(retval))
