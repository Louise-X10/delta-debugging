#!/bin/bash

arvo
SEED=3755726029 # May be dfferent
CRASH_INPUT=/src/commons-codec/crash-1164d98e38e204f6f44910b1017b272208c0cd1f # Reproduced with ARVO, filename may be different
# CRASH_INPUT=/src/commons-codec/clusterfuzz-testcase-minimized-PhoneticEngineFuzzer-6726368628703232 # Downloaded from OSS Fuzz
echo -n Hello > hello.bin
VALID_INPUT=/src/commons-codec/hello.bin
TARGET=PhoneticEngineFuzzer
# Can ensure this is the crashing input by reproducing the crash:
# PhoneticEngineFuzzer $CRASH_INPUT

git clone https://github.com/Louise-X10/delta-debugging.git
cd delta-debugging/examples
python3 example_ddmod4.py $CRASH_INPUT $VALID_INPUT $TARGET

# Crashing input (reproduced with ARVO):
# b'%eeeeee7%'
# Minimal crashing input:
# b'%eeeeee7%'
# Valid input:
# b'Hello'
# Maximal crashing input:
# b'Helloee7%'

# Minimized distance to valid input is:  4
# Original distance to valid input is:  12