#!/bin/bash

# This script automates the creation of fresh .ot data
# (ot-clean-data/.ot).
# See also this gist: https://gist.github.com/0x01--/25174df5f095d128e5da

# current dir
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


OT_FOLDER=~/.ot
OT_TARGET_FOLDER=$DIR/ot-clean-data

rm -rf $OT_FOLDER
# workaround for currently broken `opentxs changepw`
opentxs --dummy-passphrase changepw
(cd python3 && python3 -c "from pyopentxs import server; server.setup(open('../test-data/sample-contracts/localhost.xml'))" | opentxs-notary --only-init)


# delete folder if it exists
if [ -d "$DIR/ot-clean-data/.ot" ]; then
    rm -rf $DIR/ot-clean-data/.ot
fi

mv $OT_FOLDER $OT_TARGET_FOLDER/
