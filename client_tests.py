#import nose

import pyopentxs


def pseudonym_exists(nym_id):
    pass

def test_create_pseudonym():
    keysize = 1024
    nym_id_source = "" # optional argument
    alt_location = "" # optional argument

    nym_id = pyopentxs.create_pseudonym(
            keysize,
            nym_id_source,
            alt_location)

    assert pseudonym_exists(nym_id)
