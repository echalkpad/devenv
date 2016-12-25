#! /bin/bash
adb shell << EOF
cat /proc/kmsg
EOF
