#!/bin/bash

arvo
CRASH_INPUT=/src/clusterfuzz-testcase-minimized-read_pem-5632355033677824
SEED=01270d57eecae64f59b9b27cc06e3f9eaf2304e2 
TARGET=read_pem
VALID_INPUT=/src/boringssl/fuzz/${TARGET}_corpus/$SEED

git clone https://github.com/Louise-X10/delta-debugging.git
cd delta-debugging/examples
python3 example_ddmod3.py $CRASH_INPUT $VALID_INPUT $TARGET

# Crashing input:
# b' '
# Minimal crashing input:
# b' '
# Valid input:
# b'-----BEGIN O--------'
# Maximal crashing input:
# b'----- '