
- device model 관련 강의자료. 각 컴포넌트의 관계파악.  
http://www.cs.fsu.edu/~baker/devices/notes/ch14.html#(1)  


- 한글 문서 두가지.  
file:///home/ji-hun-kim/Documents/3._KelpLdm.pdf
file:///home/ji-hun-kim/Documents/03.kernel_device_model_print용.pdf

- LDD-3
http://www.makelinux.net/ldd3/?u=chp-14-sect-4
http://www.makelinux.net/ldd3/chp-14-sect-1



- __BUS SUBSYSTEM__
참고 : https://kldp.org/node/129971   

```
vers/base/bus.c 가 bus
글쓴이: bushi 작성 일시: 월, 2012/02/20 - 6:24오후
drivers/base/bus.c 가 bus subsystem 의 핵심이고,
가장 단순한 형태의 응용이 platform bus 라는 가상 bus 에 대한
구현(drivers/base/platform.c) 입니다.
평범한 응용을 꼽자면 PCI bus 에 대한 구현(drivers/pci/pci-driver.c) 를 들 수
있고,
약간의 기교를 더 부린 응용이 USB bus 에 대한 구현(drivers/usb/core/usb.c) 이라
할 수 있고,
기술로써 예술의 경지를 보여주는 응용이 I2C bus 에 대한
구현(drivers/i2c/i2c-core.c) 이라 생각합니다.

bus_register() 후,
device_register() 혹은 driver_register() 시점에서
bus_type.match() 콜백이 불린다음 bus_type.probe() 콜백이 호출되고,
호출된 bus_type.probe() 콜백에서 i2c_driver.probe() 따위의 드라이버 콜백이 다시
호출되고,
드라이버 콜백에서 각자 고유한 어떤 일이 행해집니다.
```

device와 driver의 의미  
http://forum.falinux.com/zbxe/index.php?document_srl=567697&mid=device_driver  





device tree

https://lwn.net/Articles/448502/
https://kerneltweaks.wordpress.com/2014/03/30/platform-device-and-platform-driver-linux/
https://kerneltweaks.wordpress.com/2014/11/27/the-story-of-device-tree-for-platfrom-device/

