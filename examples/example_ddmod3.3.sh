#!/bin/bash
CRASH_INPUT=/src/clusterfuzz-testcase-minimized-ssl_ctx_api-5807097051611136
SEED=009f7a3df2effc9612a913d269fd0b4598ca7f8c 
TARGET=ssl_ctx_api
VALID_INPUT=/src/boringssl/fuzz/${TARGET}_corpus/$SEED


git clone https://github.com/Louise-X10/delta-debugging.git
cd delta-debugging/examples
python3 example_ddmod3.py $CRASH_INPUT $VALID_INPUT $TARGET

# Crashing input:
# b'-'
# Minimal crashing input:
# b'-'
# Valid input:
# b"\x16\x07;:;\xe1nono!\x16';-z:-:'\x8c)\xb7*;G\x8e*\x97;():!)\x86\xc2%\xa8'(\xd7(:(\x1b*\xe1nono!\x16';-z:-:'\x8c\xb7*;G\x8e*\x97;(\x8c;Y3(&\xaf\xaa(J\r\xa2:%::!;:\x82D!v):!)\x86\xc2%!\xa8'*\xd5@n(:\xa7z'\x14rU\xb7*\xa8''\xb7*\xa8(\xb3" 
# Maximal crashing input:
# b';:\x16\x07;-'