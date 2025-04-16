#!/bin/bash

server "$1"
STATUS=$?

if [ $STATUS -ne 0 ]; then
  exit 1
fi

# If this input is known to crash:
# Return non-zero when matching crashing input
cmp -s "$1" "$CRASH_INPUT" && exit 1

# Otherwise: success
exit 0
