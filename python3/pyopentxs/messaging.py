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


def mail_count(nym, outgoing=False):
    if outgoing:
        return opentxs.OTAPI_Wrap_GetNym_OutmailCount(nym._id)
    else:
        return opentxs.OTAPI_Wrap_GetNym_MailCount(nym._id)


def remote_mail_count(server_id, nym, outgoing=False):
    otme.retrieve_nym(server_id, nym._id, True)
    return mail_count(nym, outgoing)


def get_mail(server_id, nym, index, outgoing=False):
    (get_contents, get_other) = (
        opentxs.OTAPI_Wrap_GetNym_OutmailContentsByIndex,
        opentxs.OTAPI_Wrap_GetNym_OutmailRecipientIDByIndex
    ) if outgoing else (
        opentxs.OTAPI_Wrap_GetNym_MailContentsByIndex,
        opentxs.OTAPI_Wrap_GetNym_MailSenderIDByIndex
    )
    content = get_contents(nym._id, index)
    contact = Nym(server_id, get_other(nym._id, index))
    return Message(
        content,
        server_id=server_id,
        from_nym=nym if outgoing else contact,
        to_nym=contact if outgoing else nym)


def delete_mail(nym, index, outgoing=False):
    remove = (opentxs.OTAPI_Wrap_Nym_RemoveOutmailByIndex if outgoing
              else opentxs.OTAPI_Wrap_Nym_RemoveMailByIndex)
    assert remove(nym._id, index)


def delete_all_mail(nym, count=None, outgoing=False):
    for i in range(count or mail_count(nym, outgoing)):
        delete_mail(nym, i, outgoing)


def get_all_mail(server_id, nym, delete_from_server=False, outgoing=False):
    count = remote_mail_count(server_id, nym, outgoing)
    messages = [get_mail(server_id, nym, index, outgoing) for index in range(count)]
    if delete_from_server:
        delete_all_mail(nym, count, outgoing)
    return messages
