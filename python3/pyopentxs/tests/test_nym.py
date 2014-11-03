from pyopentxs.nym import Nym


def test_register_nym():
    Nym().register()


def test_delete_nym():
    Nym().register().delete()


def test_reregister_nym():
    n = Nym().register()
    n.delete()
    n.register()
