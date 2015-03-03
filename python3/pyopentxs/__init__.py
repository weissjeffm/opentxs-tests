import opentxs
from contextlib import closing
import os
import time

# OTME = OpenTransactions MadeEasy
otme = opentxs.OT_ME()

# The directory where OT stores its state
config_home = os.environ['HOME'] + "/.ot/" + str(time.time())
client_config_dir = config_home + "/.ot/"
notary_config_dir = os.environ['HOME'] + "/.ot/"


class ReturnValueError(BaseException):
    """
    The return value of an API function has signaled an error condition
    """
    def __init__(self, return_value):
        self.return_value = return_value

    def __str__(self):
        return "API function has returned error value %r" % self.return_value


class DummyPassphraseCallback(opentxs.OTCallback):
    def __init__(self, passphrase):
        self.passphrase = passphrase

    def runOne(self, pw):
        pw.setPassword(self.passphrase)

    def runTwo(self, pw):
        pw.setPassword(self.passphrase)


def decode(stream):
    ''', and return as string'''
    with closing(stream):
        decoded = opentxs.OTAPI_Wrap_Decode(stream.read(), True)
    return decoded


def is_message_success(message):
    '''Returns true if message has success=true'''
    if message == '':
        raise ReturnValueError(message)
    else:
        return opentxs.OTAPI_Wrap_Message_GetSuccess(message) == 1


def _remove_pid():
    """
    Remove the PID file if one exists
    """

    # There should not be a long-running opentxs client running anyway.
    # An existing PID file probably indicates a crashed process, not a running
    # instance
    pid_file = os.path.expanduser(client_config_dir + "client_data/ot.pid")
    if os.path.exists(pid_file):
        #print("removing lockfile %s" % pid_file, file=sys.stderr)
        os.remove(pid_file)


def init():
    """
    Initialize the OTAPI in order to get a working state
    """
    # This should only be done once per process.
    if not os.path.exists(client_config_dir):
        os.makedirs(client_config_dir)
    _remove_pid()
    opentxs.OTAPI_Wrap_SetHomeFolder(config_home)
    caller = opentxs.OTCaller()
    caller.setCallback(DummyPassphraseCallback("test"))
    opentxs.OT_API_Set_PasswordCallback(caller)
    opentxs.OTAPI_Wrap_Wallet_ChangePassphrase()
    opentxs.OTAPI_Wrap_AppInit()
    opentxs.OTAPI_Wrap_LoadWallet()


def cleanup():
    opentxs.OTAPI_Wrap_AppCleanup()
