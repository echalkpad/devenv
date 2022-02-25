
## 1. SD 카드 포맷  

````sh
 $ df -h   --> 장치정보확인
 $ sudo fdisk /dev/sdc
 	d 1 d 2 w
````

## 2. 바이너리 writing to SD card  
````sh
 $ sudo dd bs=1M if=RuneAudio_rpi_0.3-beta_20141029_2GB.img of=/dev/sdc
````
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

0.4 내부 네트워크 설정-> 수동 IP 할당 설정 -> 해당하는것 추가  
> 공유기 다시접속되어도 Mac 주소에해당하는 ip주소는 고정.  


## ssh 접속 문제

````log
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
````
> 라고 나올때는 기존에 접속하던 주소의 SSH서버와 RSA 키가 맞지 않아서 생긴 문제.  -> OS를 다시설치해서 그럼.  
> remove with: ssh-keygen -f "/home/jihuun/.ssh/known_hosts" -R 192.168.0.9  
> 이렇게 위에나온대로 지워주면 됨.  


## 6 공유기 설정 : 여러 기기 접속시키기  
공유기 접속 -> 포트포워드 설정 + 강제 IP 할당 : 이두가지만 하면 됨.  
위에서 DMZ 설정은 모든 포트를 열어두는것이기 때문에 지금까지접속이 되엇던것임, 보안취약.  
외부에서 접속할때 포트까지 지정해서 접속해야됨.  
포트포워드 설정은 외부 포트는 5580 내부포트는 80 으로 지정(웹접속)  
내부포트는 웹접속일때 80 , ssh 일때는 22. 표준으로 지정되어있음.   
ssh 접속할때  
ssh -p 5522 root@procyonq.iptime.org  
이렇게 -p 옵션(포트번호지정) 을 주어야 접속이 됨.  


## 7 Rune UI 수동 업데이트  
RPI 1 의 배포판은 14년도에 릴리즈되었기때문에 rune UI가 오래된것임 수동으로 업데이트필요.  
(실제로 conneting 이 무한으로 돌고있는 버그가 있었음)  

수동 없데이트 방법 :  
http://www.runeaudio.com/documentation/troubleshooting/updating/

1) ssh 접속  
2) cd /var/www  
3) git pull  
	해당 디렉토리의 파일들은 git server의 로컬 리포로 되어있어서 pull로 최신 버전으로 땡김.  
4) curl -s -X GET 'http://localhost/clear'  
	이게 무슨 역할인지 잘 모름.  


## 8 mac 에서 ssh 로 접속하기

Mac 에선 이런식으로 접속이 안됨  
````bash
 $ ssh root@procyonq.iptime.org:5522

````

이렇게 해야함  
````bash
 $ ssh -l root -p 5522 procyonq.iptime.org

````

내 PC 접속 환경
````bash
# rune audio 접속 , rune
 $ ssh -l root -p 5522 procyonq.iptime.org

# Ubuntu 접속
 $ ssh -l jihuun -p 4422 procyonq.iptime.org

````
