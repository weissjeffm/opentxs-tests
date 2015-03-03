#!/usr/bin/env python3
import shutil
import os
import sys
import pytest
import pyopentxs
from pyopentxs import notary
import subprocess


def create_fresh_ot_config():
    if os.path.exists(pyopentxs.notary_config_dir):
        shutil.rmtree(pyopentxs.notary_config_dir)

    # create a client wallet just for making the server contract
    #os.system("opentxs --dummy-passphrase changepw")

    # create server contract and empty the client side data
    setup_data = notary.setup(open('../test-data/sample-contracts/localhost.xml'), total_servers=2)
    p = subprocess.Popen(["opentxs-notary", "--only-init"], stdin=subprocess.PIPE)
    outs, errs = p.communicate(input=setup_data.getvalue(), timeout=20)

    # set cron interval to shorter than default
    config_data = notary.config.read()
    config_data['cron']['ms_between_cron_beats'] = '2500'  # in milliseconds
    notary.config.write()


def fresh_setup():
    '''opentxs-notary must be on the PATH'''

    create_fresh_ot_config()
    print("created fresh config, restarting...")
    notary.restart()
    print("restarted.")
    # wait for ready
    # doesn't seem to be necessary
    # time.sleep(2)


if __name__ == "__main__":
    fresh_setup()
    pytest.main(sys.argv[1:])
    pyopentxs.cleanup()
