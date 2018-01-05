# After computer was rebooted, you should issue below commands.
#! /bin/bash

LFS=/mnt/lfs

sudo mount -v -t ext4 /dev/sdb5 $LFS

sudo mount -v --bind /dev $LFS/dev

sudo mount -vt devpts devpts $LFS/dev/pts -o gid=5,mode=620
sudo mount -vt proc proc $LFS/proc
sudo mount -vt sysfs sysfs $LFS/sys
sudo mount -vt tmpfs tmpfs $LFS/run

sudo chroot "$LFS" /usr/bin/env -i              \
	HOME=/root TERM="$TERM" PS1='\u:\w\$ ' \
	PATH=/bin:/usr/bin:/sbin:/usr/sbin     \
	/bin/bash --login
