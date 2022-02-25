  
  
## 0. 환경 구축.  
  
  
## 1. 모듈 빌드 환경  
  
### 1.1 RPI-2 기준 kernel 빌드.   
  
- 빌드 유틸 설치  
  
```bash  
 $ git clone https://github.com/raspberrypi/tools  
```  
  
- .bashrc에 위에서 받은 툴 환경변수 경로 지정.  
  
```bash  
 $HOME/study/linux/rpi/tools/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian-x64/bin  
```  
  
- RPI kernel code 받기  
  
```bash  
 $ git clone https://github.com/raspberrypi/linux make bcm2709_defconfig  
```  
  
- .config 생성  
  
```bash  
 $ make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- bcm2709_defconfig  
```  
  
- 빌드  
  
```bash  
$ make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- zImage modules dtbs  
```  
> 이후 vmlinux , zImage 생성 확인.    
  
  
### 1.2 RPI-2 기준 모듈 빌드 환경 구축  
  
- Makefile 생성  
  
```makefile  
obj-m = module_test.o  
  
default :  
	make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- -C /home/ji-hun-kim/study/linux/rpi/linux SUBDIRS=/home/ji-hun-kim/link/ldd3/examples modules   
```  
> 크로스 빌드를 해야하기 때문에 아래의 옵션을 꼭 적어줘야함.  
> ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf-  
> 안해서 계속 에러 났었음.    
  
  
- simple 모듈 소스파일 생성  
module_test.c  
  
```c  
#include <linux/init.h>  
#include <linux/module.h>  
  
MODULE_LICENSE("Dual BSD/GPL");  
  
static int hello_init(void)  
{  
	    printk(KERN_ALERT "Hello, world\n");  
	        return 0;  
}  
  
static void hello_exit(void)  
{  
	    printk(KERN_ALERT "Goodbye, cruel world\n");  
}  
  
module_init(hello_init);  
module_exit(hello_exit);  
```  
  
- make !  
  
```bash  
ji-hun-kim@jihuun:~/link/ldd3/examples$ make  
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- -C  
/home/ji-hun-kim/study/linux/rpi/linux  
SUBDIRS=/home/ji-hun-kim/link/ldd3/examples modules   
make[1]: Entering directory `/home/ji-hun-kim/study/linux/rpi/linux'  
  CC [M]  /home/ji-hun-kim/link/ldd3/examples/module_test.o  
  Building modules, stage 2.  
  MODPOST 1 modules  
  CC      /home/ji-hun-kim/link/ldd3/examples/module_test.mod.o  
  LD [M]  /home/ji-hun-kim/link/ldd3/examples/module_test.ko  
make[1]: Leaving directory `/home/ji-hun-kim/study/linux/rpi/linux'  
```  
  
```bash  
ji-hun-kim@jihuun:~/link/ldd3/examples$ ls  
Makefile        module_test.c   module_test.mod.c  module_test.o  
Module.symvers  module_test.ko  module_test.mod.o  modules.order  
```  
모듈 빌드 성공.    
  
  
  
### 1.2 RPI-2 에 모듈 적재 해보기  
  
- rpi에 raspbian 설치.  
- rpi 파일 시스템에 모듈빌드 산출물 module_test.ko 복사하고   
  
`insmode module_test.ko` 했더니   
```bash
 $ insmode module_test.ko
 Error: could not insert module hello_world.ko: Invalid module format  
```  
원인은? 모듈빌드 할때 사용했던 커널 소스코드와 RPI에 있는 커널 헤더 버전이 안맞아서임.  
인터넷에서 다운받은 raspbian 을 그대로 사용했기때문에 예전 버전 커널임.
참고 )    
http://stackoverflow.com/questions/21244481/error-using-insmod-could-not-insert-module-hello-world-ko-invalid-module-forma    
-->> 더 알아보기.  
  
  
- 따라서 로컬 빌드한 커널바이너리로 RPI 에 넣고 부팅시켜야함.  
  
RPI용 커널 빌드는 아래 링크 참고  
https://www.raspberrypi.org/documentation/linux/kernel/building.md  
  
sdcard 삽입 후 (/media/에 mount 된다고 가정)  

```bash  
# 기존에 있던 커널 이미지 백업  
mv /media/boot/kernel7.img /media/boot/kernel7.img.back  
  
# 빌드완료된 zImage를 kernel7.img로 이름 변경하여 복사  
cp $YOUR_RPI_SRC/arch/arm/boot/zImage /media/boot/kernel7.img  
```  
  
이 후 RPI재부팅 해서, 아래와같이 테스트시 정상동작 확인!!  
```bash  
# 커널 변경 확인   
 $ uname -r   
 4.1.15-v7*  
  
# module 올리기  
 $ sudo insmod module_test.ko  
 Hello, world  
  
# module 적재 확인  
 $ lsmod  
 Module			Size	Used by  
 module_test		798	0  
  
# dmesg 로 module 에서 출력한 printk메시지 확인.  
 $ dmesg  
 ...  
 [ 52.22344] Hello, world  
  
# module 제거  
 $ sudo rmmod module_test  
 Goodbye, cruel world  
  
```  
정상 동작 확인 됨!!!  
  
  
  
  
  
## 2. 모듈 만들기.  
  
  
```bash  
```  

### 2.3 Kernel Modules VS Applications

Kernel Module :  kernel 메모리영역 사용, concurrency 등 고려해야할 게 많음.  멀티 프로세스 사용할때도  
Application : virtual 메모리 영역 사용. 

- 기타  

user 프로그램과 다르게 kernel 영역에는 stack이 매우 적게 사용된다 (4096-byte
page) 그렇기 때문에 드라이버를 작성할때, stack을 적게 사용하도록 프로그래밍
해야함.  

"__" 로 시작하는 함수는. 사용할때 매우 주의를 요하는 함수라는 의미이다.  

커널 코드는 floating point 산술 연산을 못함.(할 필요가 없어서)  

