while
do
	echo 1057000 > /sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq
	echo 1057000 > /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq
	echo 528000 > /sys/class/devfreq/devfreq-ddr/min_freq
	echo 528000 > /sys/class/devfreq/devfreq-ddr/max_freq
	echo 468 > /sys/devices/platform/soc.2/d4200000.axi/mmp-disp/freq
	sleep 4
	echo 624000 > /sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq
	echo 1248000 > /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq
	echo 156000 > /sys/class/devfreq/devfreq-ddr/min_freq
	echo 528000 > /sys/class/devfreq/devfreq-ddr/max_freq
	echo 451 > /sys/devices/platform/soc.2/d4200000.axi/mmp-disp/freq
	sleep 4
	echo 499 > /sys/devices/platform/soc.2/d4200000.axi/mmp-disp/freq
	sleep 4
	echo 451 > /sys/devices/platform/soc.2/d4200000.axi/mmp-disp/freq
	sleep 4


done
