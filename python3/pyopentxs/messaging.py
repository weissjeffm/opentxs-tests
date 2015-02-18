from pyopentxs import otme, ReturnValueError
from pyopentxs.nym import Nym
import opentxs


class Message:
    def __init__(self, content, server_id=None, from_nym=None, to_nym=None):
        self.content = content
        self.server_id = server_id
        self.from_nym = from_nym
        self.to_nym = to_nym

    def send(self, server_id=None, from_nym=None, to_nym=None):
        response = otme.send_user_msg(server_id or self.server_id,
                                      (from_nym and from_nym._id) or self.from_nym._id,
                                      (to_nym and to_nym._id) or self.to_nym._id,
                                      self.content)
        if response == "":
            raise ReturnValueError("Error sending message to {}".format(to_nym))

    def __repr__(self):
        return "<Message from_nym={}, to_nym={}, content='{}''>".format(
            self.from_nym, self.to_nym, self.content)

    def __eq__(self, other):
        return (self.content == other.content and
                self.server_id == other.server_id and
                self.from_nym == other.from_nym and
                self.to_nym == other.to_nym)


def mail_count(nym):
    return opentxs.OTAPI_Wrap_GetNym_MailCount(nym._id)


def remote_mail_count(server_id, nym):
    otme.retrieve_nym(server_id, nym._id, True)
    return mail_count(nym)


def get_mail(server_id, nym, index):
    content = opentxs.OTAPI_Wrap_GetNym_MailContentsByIndex(nym._id, index)
    from_nym = Nym(server_id, opentxs.OTAPI_Wrap_GetNym_MailSenderIDByIndex(nym._id, index))
    return Message(content, server_id=server_id, from_nym=from_nym, to_nym=nym)


def delete_mail(nym, index):
    assert opentxs.OTAPI_Wrap_Nym_RemoveMailByIndex(nym._id, index)


def delete_all_mail(nym, count=None):
    for i in range(count or mail_count(nym)):
        delete_mail(nym, i)


def get_all_mail(server_id, nym, delete_from_server=False):
    count = remote_mail_count(server_id, nym)
    messages = [get_mail(server_id, nym, index) for index in range(count)]
    if delete_from_server:
        delete_all_mail(nym, count)
    return messages
