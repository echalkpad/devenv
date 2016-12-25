#! /bin/bash
adb shell << EOF
	echo $1 > /sys/devices/platform/soc.2/d4200000.axi/mmp-disp/freq
	exit
EOF
