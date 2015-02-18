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
    assert len(bobinbox) == 1
    bobmsg = bobinbox[0]
    assert bobmsg == alicemsg
    messaging.delete_all_mail(bob)
    assert messaging.mail_count(bob) == 0


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
