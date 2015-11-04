
## 1. SD 카드 포맷  

```sh
 $ df -h   --> 장치정보확인
 $ sudo fdisk /dev/sdc
 	d 1 d 2 w
```

## 2. 바이너리 writing to SD card  
```sh
 $ sudo dd bs=1M if=RuneAudio_rpi_0.3-beta_20141029_2GB.img of=/dev/sdc
```
> 시간이 쫌 걸림.  


## 3. 접속확인  
1. 공유기에 접속해서 어느 IP로 라즈베리파이가 할당되었는지 확인 후  
$ ssh root@192.168.0.9  
passwd : rune  
2. 브라우져에서 192.168.0.9  접속  

## 4. 음악 라이브러리 추가  
1. USB 에 음악넣고 RPI에 삽입 끝  
2. PC 에 저장된 음악 네트워크로 하기. -> 잘 안됨.  

## 5. 공유기 ddns기능으로 외부 에서 접속하기.  
iptime 설정  
0. 고급설정->
0.1 특수기능 -> DDNS설정 -> 등록  (procyonq.iptime.org)  
0.2 보안기능 -> 공유기접속관리 -> 원격관리포트사용 (4자리입력:가령2222)  
0.3 NAT/라우터 관리->DMZ/twin ip설정 -> DMZ 선택후 R-PI ip입력  
> (procyonq.iptime.org) 로 접속하면 바로 R-pi로 연결됨.  
> (procyonq.iptime.org:2222) 로 접속하면 공유기설정화면으로 연결됨. (0.2설정때문)  




## ssh 접속 문제

```log
jihuun@jihuun-pc:~$ ssh root@192.168.0.9
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
IT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY!
Someone could be eavesdropping on you right now (man-in-the-middle attack)!
It is also possible that a host key has just been changed.
The fingerprint for the ECDSA key sent by the remote host is
04:7e:6f:15:fd:11:47:40:37:46:5e:85:a7:c8:e9:e8.
Please contact your system administrator.
Add correct host key in /home/jihuun/.ssh/known_hosts to get rid of this message.
Offending ECDSA key in /home/jihuun/.ssh/known_hosts:1
  remove with: ssh-keygen -f "/home/jihuun/.ssh/known_hosts" -R 192.168.0.9
  ECDSA host key for 192.168.0.9 has changed and you have requested strict checking.
  Host key verification failed.
```
> 라고 나올때는 기존에 접속하던 주소의 SSH서버와 RSA 키가 맞지 않아서 생긴 문제.  -> OS를 다시설치해서 그럼.  
> remove with: ssh-keygen -f "/home/jihuun/.ssh/known_hosts" -R 192.168.0.9  
> 이렇게 위에나온대로 지워주면 됨.  

