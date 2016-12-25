#! /bin/bash
#if [ "$1" ]; then
#	adb shell << EOF
#	echo $1 > /sys/devices/platform/soc.2/d4200000.axi/mmp-disp/freq
#	exit
#	EOF
#else
#	adb shell << EOF
#	cat /sys/devices/platform/soc.2/d4200000.axi/mmp-disp/freq
#	exit
#	EOF
#fi

adb shell << EOF
cat /sys/devices/platform/soc.2/d4200000.axi/mmp-disp/freq
exit
EOF
