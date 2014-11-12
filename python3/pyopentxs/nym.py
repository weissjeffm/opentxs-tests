from pyopentxs import otme, ReturnValueError, is_message_success, server
import opentxs


class Nym:
    '''Represents an OT nym'''

    def __init__(self, server_id=None, _id=None):
        self.server_id = server_id
        self._id = _id

    def create(self, keybits=1024, nym_id_source="", alt_location=""):
        """
        Create a new nym in the local wallet.

        Crashes with OT_FAIL if keysize is invalid.

        Returns the nym object
        """
        retval = otme.create_nym(keybits, nym_id_source, alt_location)

        if retval == '':
            # the nym id should be a 43-byte hash
            raise ReturnValueError(retval)
        self._id = retval
        return self

    def set_name(self, name, signer_nym_id=None):
        success = opentxs.OTAPI_Wrap_SetNym_Name(self._id, signer_nym_id or self._id, name)
        if not success:
            raise ReturnValueError("Could not set nym name to {}")

    def get_name(self):
        return opentxs.OTAPI_Wrap_GetNym_Name(self._id)

    def register(self, server_id=None):
        '''Registers the nym with the given server.  If there is no nym id yet
           (this object is still empty), the nym data will be created
           with defaults first, and then registered to the server.
           Returns the nym object.

        '''
        server_id = server_id or self.server_id or server.first_active_id()
        assert server_id, "Can't register a nym without a server id.'"
        self.server_id = server_id
        if not self._id:
            self.create()
        message = otme.register_nym(server_id, self._id)
        assert is_message_success(message)
        print(message)
        return self

    def delete(self):
        deleted = opentxs.OTAPI_Wrap_deleteUserAccount(self.server_id, self._id)
        print("deleting {} returned {}".format(self._id, deleted))
        if deleted <= 0:
            raise ReturnValueError("Unable to delete nym {}, return code {}".format(
                self._id, deleted))

    def name(self):
        """
        Return the nym name for a given id.

        Attention: If the nym for the id cannot be found, an empty string is
        returned.
        """

        # FIXME: test and fix crash for empty _id
        # FIXME: discern between "empty name" and "nym not found"
        assert self._id, "Can't get name of an empty Nym'"
        nym_name = opentxs.OTAPI_Wrap_GetNym_Name(self._id)

        if nym_name == '':
            raise ReturnValueError(nym_name)

        return nym_name

    def __repr__(self):
        return "<Nym id={}, server_id={}>".format(self._id, self.server_id)


def get_all():
    """
    Return list of locally stored nyms.
    """
    nym_count = opentxs.OTAPI_Wrap_GetNymCount()
    nyms = []
    for i in range(nym_count):
        nym_id = opentxs.OTAPI_Wrap_GetNym_ID(i)
        if nym_id == '':
            # this is just a guess, a _id should never be an empty string
            raise ReturnValueError(nym_id)
        nyms.append(Nym(_id=nym_id))
    return nyms


def check_user(server, nym, target_nym):
    # TODO
    # see ot wiki "API" / "Write a checkque"
    return otme.check_user(server, nym, target_nym)
