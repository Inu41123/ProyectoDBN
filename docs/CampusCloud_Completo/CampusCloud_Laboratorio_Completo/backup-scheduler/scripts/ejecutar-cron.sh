#!/bin/sh
set -eu
exec /usr/bin/python3 -c '
import os
with open("/proc/1/environ", "rb") as f:
    for entry in f.read().split(b"\0"):
        if b"=" in entry:
            key, value = entry.split(b"=", 1)
            os.environ[os.fsdecode(key)] = os.fsdecode(value)
os.execvpe("/bin/sh", ["/bin/sh", "/scripts/backup-semanal.sh"], os.environ)
'
