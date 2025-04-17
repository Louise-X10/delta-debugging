#!/bin/bash
VALID_INPUT=/src/boringssl/fuzz/server_corpus/$SEED

arvo
SEED=3755726029 # May be dfferent
CRASH_INPUT=crash-1164d98e38e204f6f44910b1017b272208c0cd1f # May be different
echo -n Hello > hello.bin
# Can ensure this is the crashing input by reproducing the crash:
# PhoneticEngineFuzzer $CRASH_INPUT
git clone https://github.com/Louise-X10/delta-debugging.git
cd delta-debugging/examples
apt-get install -y python3
VALID_INPUT=../../commons-codec/hello.bin
CRASH_INPUT=../../commons-codec/crash-1164d98e38e204f6f44910b1017b272208c0cd1f
python3 example_ddmod4.py $CRASH_INPUT $VALID_INPUT PhoneticEngineFuzzer