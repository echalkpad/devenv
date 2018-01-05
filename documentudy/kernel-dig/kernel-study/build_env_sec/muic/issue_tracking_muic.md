





---------------
## [ JAVA ] : RT8973 , SM5504


#### 공정에서 CP uart 가 안됨  

- 문제 : 공정에서 CP uart 가 안됨
- 원인 :  
1. JAVA의 경우 JOON, JOSHUA와는 다르게, CP uart path가 MUIC의 USB pin에만 연결되어 있습니다.
따라서, CP단 RF공정을 위해 필요한 UART Path연결시
MUIC 내부 path를 manual하게 USB로 변경하는 추가 작업이 필요 합니다

2. 1을 해도 정상동작 안함 -> AT+MODECHAN=0,0 할때, uart_sel 이 호출되어야하는데
호출안됨.

3. 2원인은 공정의 관련 Feature가 enable되어 있지 않았었음.

- 해결 : CL @7482418





### - SM5504 포팅시 문제

#### - 부트로더 포팅시 JIG_UART_OFF 케이블 연결시 중간부터 Log가 안나옴
- 문제
부트로더 포팅시 JIG_UART_OFF 케이블 연결시 중간부터 Log가 안나옴
- 원인
0x02 reg(CONTROL)의 [3]bit인 ID_SW 가 1이될때 log가 죽음
- 해결
MUIC_AUTO_SWITCH config를 enable해야함.
-> 0x02 [3]bit 0으로 유지함.  
sboot에서 sm5504 포팅할때는 무조건 해야하는듯.


#### 부트로더에서 업로드 모드 이전에 uart설정 해야함. 160225
- 문제
sboot upload mode 진입 이전에 uart path설정이 안되어있으면 AST_UPLOAD log를
출력못함. 검증 DFC? 에서 해당로그를 체크하므로 필요함.  
- 해결
muic_api_switch_to_uart() 함수 구현  
(muic path를 강제로 uart로 변경)
이후 upload모드 진입 전에 usb path로 다시 변경하는 코드 있음.  

#### 부트로더에서 rt8973 muic id Read하는 부분 수정함. 160225


#### - JIG 케이블과 VBUS가 있을때 정상 인식 안됨 160224
- 문제
JIG 케이블과 VBUS가 있을때 정상 인식 안됨
- 원인
코드상 에러
vbus flag가 반대로 되어있었음
- 해결
drivers/muic/rt8973.c  
```patch
-	vbvolt = (int2 & INT_UVLO_MASK);
+	vbvolt = !(int2 & INT_UVLO_MASK);
```


> 160226 금





---------------
## [ JOON ] : s2mu005


#### - s2mu005 에서 배터리 분리하고 JIG 로 부팅시, power off됨. 
참고로 현재 s2mu005는 manual switching 으로 설정되어있음(0xB2[2] : 0임)

-문제
s2mu005 에서 배터리 분리하고 JIG 로 부팅시, power off됨. 
-원인
불명확?
-해결
0xB2[2]를 manual switching으로 설정하기 이전에 0xB5[0]을 1로 set 
0xB5[0] (1: JIGB pin low -> JIGB ON)

#### - uart path를 ap 에서 cp로 변경하는 기능을 muic에서 switch sel이라는
독립적인 드라이버로 옮김.








---------------
## [ MediaTek ]

### - OTG 동작 문의 160225

- 문의사항  
OTG인식 방법.    
MTK reference 회로도는 OTG 인식을 위해 IDDIG 연결을 하는 것으로 되어 있는데,
삼성은 MUIC에서 OTG를 인식 후 int 발생하여 AP가 MUIC의 해당 Register을 읽은 후
AP에서 OTG 관련 drv을 올리는 것으로 구현하려고 하는데, 문제가 없는지 확인 부탁드립니다. 
- 답변  
OTG인식을 위해 추가 GPIO 연결 필요 없이
MUIC에서 OTG 인식이 가능하며 그 동작 순서는 아래와 같습니다. 

```
 1. 케이블 연결시 MUIC 드라이버에서(Register값 또는 ADC값 확인하여) 케이블 인식.
	(OTG인식) 그리고 필요시 내부 Path 설정
 2. MUIC 드라이버에서 USB 드라이버로 인식된 케이블 종류를 전달 해줌 (notifier call)
 3. USB드라이버에서 OTG 관련내용 처리 
```


