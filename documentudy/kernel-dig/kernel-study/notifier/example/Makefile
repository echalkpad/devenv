obj-m += noti_reg.o callchain1_reg.o callchain2_reg.o callchain.o
KDIR:=/home/mogin/s3c2440/linux-2.6.33_usb0

.PHONY: clean

all:
	make -C $(KDIR) SUBDIRS=$(PWD) modules

clean:
	make -C $(KDIR) SUBDIRS=$(PWD) clean

