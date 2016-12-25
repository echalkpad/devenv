#! /bin/bash
adb shell << EOF
cat /sys/bus/platform/drivers/mmp_dsi/d420b800.dsi/adaptive_fps
exit
EOF
