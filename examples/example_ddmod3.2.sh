#!/bin/bash
CRASH_INPUT=/src/clusterfuzz-testcase-minimized-server-6088352019251200
SEED=1037d8ef263682ea727da03710954173df7212ac
VALID_INPUT=/src/boringssl/fuzz/server_corpus/$SEED
TARGET=

git clone https://github.com/Louise-X10/delta-debugging.git
cd delta-debugging/examples
apt-get install -y python3
python3 example_ddmod3.py $CRASH_INPUT $VALID_INPUT $TARGET