obj-m = module_test.o

default :
	make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- -C /home/ji-hun-kim/study/linux/rpi/linux SUBDIRS=/home/ji-hun-kim/link/ldd3/examples modules
#	make -C /home/ji-hun-kim/link/joon_kernel/ SUBDIRS=/home/ji-hun-kim/link/ldd3/examples modules 
#	make -C /home/ji-hun-kim/link/joon_kernel/ M=/home/ji-hun-kim/link/ldd3/examples modules 

clean :
	make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- -C /home/ji-hun-kim/study/linux/rpi/linux SUBDIRS=/home/ji-hun-kim/link/ldd3/examples clean
