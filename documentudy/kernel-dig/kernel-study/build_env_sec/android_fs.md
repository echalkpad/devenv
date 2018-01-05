
pit파일은 바이너리를 eMMC의 각 구역아 어디에 배치할지에 대한 정보가 있음.  
PIT 파일을 특수 프로그램으로 열어보면 .bin파일과 .img파일로 나뉨.   
(android/out/target/product/모델/ 에 존재하는 빌드 산출물과 동일)  
보통 .img파일은 파일시스템이고 리눅스 로컬PC에서도 mount명령으로 해당 파일시스템을 접근할 수 있음.  

### 빌드 산출물   

안드로이드 과제에서 풀빌드를 했다면 android/out/target/product/모델/ 경로에 다음의 파일이 있음.  
AP_J110XXXX~~~.tar.md5 라는 빌드산출물은 압축된건아니고 tar로 모아진것임.  
tar -tvf AP_J???   해보면 다음의 4개의 파일로 구성되어 있다는것을 볼 수 있음.  

- `system.img` 안드로이드에서 사용하는 파일시스템으로 루트파일시스템의 /system 디렉터리에 마운트됨.  
- `boot.img` 는 커널 바이너리로   
>	1. uImage(순수 커널 바이너리) +   
>		uImage 란?   
>		 보톻 순수 리눅스 커널을 빌드하면 vmlinux 가 나오는데 이걸 압축하면 piggy.o가 나오고  head.o misc.o도 같이 합쳐서 압축해서 zImage파일을 만든다.   
>		(커널 소스의 linux/arch/아키텍쳐/boot/ 경로에 만들어짐) 삼성에선 uImage파일을 만듬.  
>		+System.map 에대해 알아보기.   
>	2. ramdisk.img (커널의 루트 파일시스템)   
>		android/out/target/product/모델/root 가 파일시스템 이미지형태로 만들어진것임.  
>	3. dt.img 가 합쳐진것   
- `recovery.img`는 리커버리 바이너리로 boot.img와 램디스크만 다르다!  
>	1. uImage ( boot.img바이너리와 같은 커널 바이너리)  
>	2. ramadisk-recovery.img   
>	3. dt.img 가 합쳐진것  
-  `NVM.img`  


### 빌드 스크립트 참고 : boot.img는 어떤 바이너리가 포함되어 있나?  

buildscript/build_conf/j1acelte/common_build_conf.j1acelte 보면  

```bash  
boot.img                  = cmd@mkbootimg kernel@kernel ramdisk@ramdisk.img dt@dt.img  
```  

buildscript/build_common/build_api/build_api.build 파일에  

```bash  
if [ "${arch}" == "arm64" ] ; then  
cp -v -f ${KERNEL_OUTPUT}/arch/${arch}/boot/uImage %(android-product-out-dir)s/kernel  
```  



### 파일시스템 마운트 방법  

#### 1.  system.img 로컬 PC에 마운트 하기.  
원래 파일시스템은 파티션의 모든 공간을 사용해야함.   
system.img는 실제 SYSTEM파티션 보다 더 작은 크기임. 빌드시 압축되며 오딘으로 단말에 다운로드 받을때 원래 크기로 압축이 풀림. 그때 사용하는 tool이 simg2img 이다.   
d/out/target/product/j1acelte/obj/PACKAGING/target_files_intermediates/j1aceltexx-target_files-J1ACELTEXX_TEST/OTA/tools/simg2img 에 있음..)  

```bash  
$ system.img를 현재 디렉터리에 복사  
$ mkdir ./system/  
$ simg2img로 system.img 압축해제  
$ simg2img system.img system.img.raw  
$ mount -t ext4 -o /dev/loop system.img.raw ./system/  

```  

#### 2. mount 명령어는  PC에 일시적으로 파일시스템을 마운트 시킬 수 있으나 PC가 재부팅되면 사라짐.  
하지만 항상 mount시킬 수 있는 방법이 있음. -> fstab파일에 작성.   
>	로컬 PC는  /etc/fstab 파일에 적혀 있고  
>	단말의 루트파일시스템에는 /fstab.pxa1908 에 적혀있음.  

 트 파일 시스템(ramdisk.img) 에 있는 (android/out/target/product/모델/root/ 디렉터리와 동일 구조)  
fstab.pxa1908 에 각 파일 시스템을 어떻게 mount할 것인지에대한 정보가 있음.  

```fstab  
<mnt_point>  <type>  <mnt_flags and options> <fs_mgr_flags>  

/dev/block/platform/soc.2/by-name/SYSTEM    /system       ext4      ro,nosuid,errors=panic                                                          wait  
/dev/block/platform/soc.2/by-name/CACHE     /cache        ext4      nosuid,nodev,noatime,noauto_da_alloc,discard,journal_async_commit,errors=panic  wait,check  
/dev/block/platform/soc.2/by-name/USER      /data         ext4      nosuid,nodev,noatime,noauto_da_alloc,discard,journal_async_commit,errors=panic  wait,check,encryptable=footer  
/dev/block/platform/soc.2/by-name/EFS       /efs          ext4      nosuid,nodev,noatime,noauto_da_alloc,discard,journal_async_commit,errors=panic  wait,check  
```  
>   
`/dev/block/platform/soc.2/by-name/????`  <- 각 eMMC 파티션의 구역 이름   
`/system`  <- 루트 파일시스템의 /system 디렉터리에 mount 한다는 뜻.  
id,errors=panic`  <- mount명령어의 옵션 (man mount참고)  


- `(참고링크)` 안드로이드 부팅 프로세스.  
http://www.androidenea.com/2009/06/android-boot-process-from-power-on.html  
http://www.slideshare.net/chrissimmonds/android-bootslides20  
