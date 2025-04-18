#!/bin/bash

arvo
SEED=3755726029 # May be dfferent
CRASH_INPUT=/src/commons-codec/clusterfuzz-testcase-minimized-LanguageStringEncoderFuzzer-6195774643634176 # Downloaded from OSS Fuzz
echo -n Hello > hello.bin
VALID_INPUT=/src/commons-codec/hello.bin
TARGET=LanguageStringEncoderFuzzer
# Can ensure this is the crashing input by reproducing the crash:
# LanguageStringEncoderFuzzer $CRASH_INPUT

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
# b'elloeeeee7%'


# Crashing input (downloaded from OSS Fuzz):
# b'WWWWWWW\x87\x87\x0b'
# Minimal crashing input:
# b'WWWWWWW\x87\x87\x0b'
# Valid input:
# b'Hello'
# Maximal crashing input:
# olHelWWWWWW\x87\x87\x0b