make clean가능하게 하기!!  

android 과제에서 빌드 할때 toolchain을 /opt/toolchain/arm-eabi-4.* 에서 사용하지
않고

android/prebuilts/ 에 존재하는 것을 이용해서 빌드함. 

그런데 LSI과제 sboot에서 obj파일 지우려고 하면 ```$ make clean```을 해야함.
그런데 아래와같은 로그와함께 안됨.

```log
Required toolchain directory /opt/toolchains/arm-eabi-4.9/bin is not present in your server. 
Makefile:78: *** Please install arm-eabi-4.9 toolchain for building bootloader.  . Stop.
```

방법은 
android/prebuilts/gcc/linux-x86 경로를 /opt/toolchain/으로 통째 복사. 

$ sudo cp -r android/prebuilts/gcc/linux-x86/ /opt/toolchains/

.bashrc 에 아래 추가.  
export CROSS_COMPILE=/opt/toolchains/linux-x86/aarch64/aarch64-linux-android-4.9/bin/aarch64-linux-android-


이제 make clean하면 이 환경변수를 먼저 찾음.  




- 이렇게 make clean하기전에 직접 지정해줘도 됨

```sh
 $ export CROSS_COMPILE=../../../prebuilts/gcc/linux-x86/aarch64/aarch64-linux-android-4.9/bin/aarch64-linux-android-
 $ make clean
```
