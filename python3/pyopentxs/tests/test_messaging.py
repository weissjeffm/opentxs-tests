import pytest
from pyopentxs.nym import Nym
from pyopentxs import messaging, server


@pytest.fixture
def friends():
    return [Nym().register() for _ in range(2)]


def test_basic_messaging(friends):
    alice, bob = friends
    s1 = server.first_active_id()
    alicemsg = messaging.Message("hi bob, foo bar baz!", from_nym=alice, to_nym=bob, server_id=s1)
    assert messaging.remote_mail_count(s1, bob) == 0
    alicemsg.send()
    bobinbox = messaging.get_all_mail(s1, bob)
    aliceoutbox = messaging.get_all_mail(s1, alice, outgoing=True)
    messaging.verify_mail(bob, 0)
    messaging.verify_mail(alice, 0, outgoing=True)
    assert messaging.get_mail_notary_id(bob, 0) == s1
    assert messaging.get_mail_notary_id(alice, 0, outgoing=True) == s1
    assert len(bobinbox) == 1
    assert len(aliceoutbox) == 1
    bobmsg = bobinbox[0]
    aliceoutboxmsg = aliceoutbox[0]
    assert bobmsg == alicemsg and bobmsg == aliceoutboxmsg
    messaging.delete_all_mail(bob)
    assert messaging.mail_count(bob) == 0
    messaging.delete_all_mail(alice, outgoing=True)
    assert messaging.mail_count(alice, outgoing=True) == 0


@pytest.mark.parametrize("content",
                         ["abcd abcd",
                          " ",
                          "我能吞下玻璃而不伤身体"])
def test_mail_content(friends, content):
    alice, bob = friends
    s1 = server.first_active_id()
    alicemsg = messaging.Message(content, from_nym=alice, to_nym=bob, server_id=s1)
    alicemsg.send()
    bobmsg = messaging.get_all_mail(s1, bob)[0]
    assert bobmsg.content == content


def test_send_many_messages(friends):
    alice, bob = friends
    s1 = server.first_active_id()
    msgs = [messaging.Message("hello bob, this is msg %s" % i,
                              from_nym=alice, to_nym=bob, server_id=s1)
            for i in range(10)]
    for m in msgs:
        m.send()
    # now make sure they're all in bob's inbox
    bobinbox = sorted(messaging.get_all_mail(s1, bob), key=lambda m: m.content)
    assert bobinbox == msgs
