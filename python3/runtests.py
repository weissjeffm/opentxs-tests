import pyopentxs
import shutil
import psutil
import os
import time
import pytest


def clean_ot_config():
    # copy the clean data directory
    if os.path.exists(pyopentxs.config_dir):
        shutil.rmtree(pyopentxs.config_dir)
    shutil.copytree("../ot-clean-data/.ot", pyopentxs.config_dir)


def restart_opentxs_notary():
    '''opentxs-notary must be on the PATH'''
    # kill existing processes
    for proc in psutil.process_iter():
        if proc.name() == "opentxs-notary":
            proc.kill()
            psutil.wait_procs([proc], timeout=10)

    # clean the config dir
    clean_ot_config()

    # start new
    os.system("opentxs-notary > opentxs-notary.log 2>&1 &")

    # wait for ready
    time.sleep(2)

if __name__ == "__main__":
    restart_opentxs_notary()
    pyopentxs.init()
    pytest.main("--junitxml=junit-report.xml")
    pyopentxs.cleanup()
