#! /bin/bash

adb push ./auto_freq.sh /data/
adb push ./lcd_onoff.sh /data/

adb shell << EOF
./data/auto_freq.sh &
./data/lcd_onoff.sh &
exit
EOF

