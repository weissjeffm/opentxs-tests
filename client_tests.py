#import nose

from nose.tools import timed

import pyopentxs

def pseudonym_exists(nym_id):
    nym_ids = pyopentxs.get_nym_ids()
    return nym_id in nym_ids

def test_create_pseudonym():
    keysize = 1024
    nym_id_source = "" # optional argument
    alt_location = "" # optional argument

    nym_id = pyopentxs.create_pseudonym(
            keysize,
            nym_id_source,
            alt_location)

    assert pseudonym_exists(nym_id), "nym_id=%r" % nym_id


#
# FIXME:
# Python can't really capture the hanging test because the whole
# process hangs. This is because opentxs often uses the OT_FAIL which
# in turn calls std::terminate(). There maybe is a way to capture that
#
# @timed(2)
# def test_capture_crash():
#     pyopentxs.get_nym_name("")

