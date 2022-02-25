# muic 구현, 구조상의 특징 정리    
  
  
### 기본 동작  
  
기본적으로 케이블이 삽입되면 REG및 ADC파악해서 케이블 종류 구분하고  
그것을 다른쪽으로 noti를 날려주는게 기본 역할 이다.  
  
두번째로 전원(vbus)이 있는지 파악해서 notifier_call 을 날려줌.  
(charger fuel gauge 에서 받음)  
  
  
- driver파일에 존재하는 함수들.  
  
1. i2c 로 register R/W 하는 api  
2. muic 초기화 함수  
3. 케이블 인터럽트시 처리 함수  
4. 기타 필요한 기능 sysfs 노드   
  
- path 연결  
MUIC IC기본 기능은 기본적으로 내부 path를 USB, UART, open 세가지 중 하나로  
연결하는 것이다.  
  
- auto config 모드  
위의 path연결을 드라이버에서 manual로 할 수 있지만 chip에서 기본적으로  
auto모드를 지원하기 때문에, 케이블 연결시 hw가 알아서 인식하여 적절한 path로  
연결한다. 따라서 auto 모드일때는 드라이버에서 path 연결 관련 코드는 수행할  
필요없음. auto 모드 셋팅은 레지스터 설정으로 함.  
  
  
### 인터럽트  
  
sm5504, rt8973 의 경우    
0x02h 0bit MASK_INT를 0으로해야 INTB pin이 동작을 함.    
인터럽트 동작은 평상시에 INTB pin이 high 를 유지하다가 케이블이 연결되면    
MUIC에서 low로 내렸다가 올림. AP에서 이를 인터럽트로 인식함.    
  
- sm5504 인터럽트 특징    
문제 : 인터럽트 핸들러가 한번만 뜸. 오실로 스코프로 INTB 라인을 찍었을때,    
처음에 케이블이 연결되면 low로 떨어진뒤 다시 high 로 올라오지 않음.    
즉 맨처음 인터럽트만 인식되고 그 뒤부터는 인터럽트 인식이 안됨.    
  
해결 : sm5504는 인터럽트 핸들러에서 0x03h 0x04h (int1, int2) 레지스터를    
read해야 INTB라인이 다시 high로 올라옴. 이유는 아직모름.    
  
### 각 인식되는 케이블 별로 MUIC 단에서 해야하는 동작은?   
-> auto 모드 일때는 할필요없는듯? manual mode 일때만  
  
1. USB path 설정  
	ATTACHED_DEV_USB_MUIC,  
	ATTACHED_DEV_CDP_MUIC,  
	ATTACHED_DEV_OTG_MUIC,  
  
	ATTACHED_DEV_JIG_USB_OFF_MUIC,  
	ATTACHED_DEV_JIG_USB_ON_MUIC,  
  
	ATTACHED_DEV_AUDIODOCK_MUIC,  
2. UART path 설정  
	ATTACHED_DEV_JIG_UART_OFF_MUIC,  
	ATTACHED_DEV_JIG_UART_OFF_VB_MUIC,	/* VBUS enabled */  
	ATTACHED_DEV_JIG_UART_OFF_VB_OTG_MUIC,	/* for otg test */  
	ATTACHED_DEV_JIG_UART_OFF_VB_FG_MUIC,	/* for fuelgauge test */  
3. open path  
	ATTACHED_DEV_TA_MUIC,  
	ATTACHED_DEV_CHARGING_CABLE_MUIC,  
  
	ATTACHED_DEV_JIG_UART_ON_MUIC,  
  
	ATTACHED_DEV_UNKNOWN_MUIC,  
  
  
  
	ATTACHED_DEV_UNOFFICIAL_ID_CDP_MUIC,  
	ATTACHED_DEV_UNDEFINED_CHARGING_MUIC,  
	ATTACHED_DEV_DESKDOCK_MUIC,  
	ATTACHED_DEV_UNKNOWN_VB_MUIC,  
	ATTACHED_DEV_DESKDOCK_VB_MUIC,  
	ATTACHED_DEV_CARDOCK_MUIC,  
  
	ATTACHED_DEV_SMARTDOCK_MUIC,  
	ATTACHED_DEV_SMARTDOCK_VB_MUIC,  
	ATTACHED_DEV_SMARTDOCK_TA_MUIC,  
	ATTACHED_DEV_SMARTDOCK_USB_MUIC,  
	ATTACHED_DEV_UNIVERSAL_MMDOCK_MUIC,  
	ATTACHED_DEV_MHL_MUIC,  
  
	ATTACHED_DEV_NUM,  
  
  
  
### 코드상 cable detect 순서  
  
1. REGISTER(device type) 확인후 처리,   
2. 1번에서 못찾으면 ADC 확인  
  
  
  
### MUIC Chip 특정  
  
- 외부 DP DM 핀을 내부 AP에 USB로 연결할건지, UART로 연결할건지, OPEN할건지  
  결정해주는 register가 있음.  
  
  
- jig on pin?  
s2mu005 에는 JIGB pin 이 있고  
0xB5h 의 0번비트가 0이면 jigb off 고 1이면 jigb on임.   
  
  
### jig는 vbus 인식을 왜하나?  
  
  
  
### 케이블 인식시 인터럽트 핸들러로  
request_threaded_irq vs work_queue 어떤게 더 적합할까?  
  
- https://lwn.net/Articles/302043/  
>> Don`t these threaded interrupt handlers have even more overhead than  
>> workqueues? Workqueues are at least handled sequentially in the same thread;  
>> using threaded interrupt handlers means there are even more context switches.   
  
> I`m afraid that you have missed a key point about real-time systems. Design of  
a hard real-time system starts with deciding which threads in the system will  
run at real-time priority (SCHED_FIFO or SCHED_RR) and also at which priority  
(1..99). This step involves all threads in the system, including threaded  
interrupt handlers. By assigning a higher priority to certain application  
threads than the threaded interrupt handlers it becomes possible to obtain a  
system with low and bounded event response time. Handling some of the interrupt  
work via workqueues instead of threaded interrupt handlers would result in a  
larger event response time.  
  
- http://stackoverflow.com/questions/15526862/clarification-about-the-behaviour-of-request-threaded-irq  
  
>> Question2: Secondly, what advantage (if any), does a  
>> request_threaded_handler approach have over a work_queue based bottom half  
>> approach ? In both cases it seems, as though the "work" is deferred to a  
>> dedicated thread. So, what is the difference ?  
  
> For Question 2, An IRQ thread on creation is setup with a higher priority,  
unlike workqueues. In kernel/irq/manage.c, you`ll see some code like the  
following for creation of kernel threads for threaded IRQs:  






### rust proof 

in LSI project

/*
 * QA`s Requirements to enable rustproof mode in a user binary:
 *  1. Check if JIG is connected
 *  2. Check if external VBAT is available
 *
 * Implementation is dependent on each projects.
 *
 *  1 : enable rustproof mode.
 *  0 : do not enable rustproof mode.
 */


BOOTLOADER 

```c
"board/mach-on5xelte.c"

# int mach_board_main(void)
| board_uart_rustproof();
| # static void board_uart_rustproof(void)
| | "0: Pin Low. Disable UART(rustproof on)
| |  1: Pin High. Enable UART(rustproof off) "
| | int ifc_sense = s5p_gpio_getpin(GPIO_IFC_SENSE_INT_AP);
| | #if defined(CONFIG_BUILD_TYPE_USER) && !defined(CONFIG_SEC_FACTORY_BUILD)
| | | g_bd.rustproof_mode = 1; /* default */
| | | if (ifc_sense)
| | | | g_bd.rustproof_mode = 0;
| | 
| | 
```


```c
"lib/bootm.c"
# static void setKernelParam(void)
| #if defined(CONFIG_USE_MUIC)
| | pmic_info |= (get_if_pmic_rev() << 4) | (check_rustproof(pmic_info) << 3);
| | ptr += sprintf(ptr, " pmic_info=%d", pmic_info);
```

```c
"drivers/muic_core.c"
# int check_rustproof(int sw_sel)
| int jig_rustproof = g_bd.rustproof_mode ^ 1;
| int param_rustproof = (sw_sel >> 3) & 1;

" switch_sel bits (xxxx_yyyy_rzzz)
  xxxx: afc disable info
  yyyy:  if pmic version.
  r : rustproof(0:on, 1:off in the Kernel)
  zzz: path infomation."
```
 



in MediaTek project


```c
snprintf(cmdline_tmpbuf, CMDLINE_TMP_CONCAT_SIZE, "pmic_info=%d", cur_param_data_int(PARAM_SWITCH_SEL));
    cmdline_append(cmdline_tmpbuf);

```

#define cur_param_data_int	get_param_env_int

# int get_param_env_int(prm_id_t id)
| return *((int *)get_param_env(id));

# void *get_param_env(prm_id_t id)
| if (IS_INT_PARAM(id))
| | return &env_file.int_param[id];


"param/host/hostenv.c"
# static int initialize_env_file(prm_env_file *pfile)
| pfile->int_param[PARAM_SWITCH_SEL] = DEFAULT_PARAM_SWITCH_SEL;

"include/config/grandpplte.h"
#define DEFAULT_PARAM_SWITCH_SEL\
		(SWITCH_AP_USB | SWITCH_AP_UART)



"app/s_boot/aboot_sec/ustar_param.c"
int set_param_env(prm_id_t id, int ivalue, char *svalue, int save)
	if (IS_INT_PARAM(id))
		env_file.int_param[id] = ivalue;


### RID 만 변경시 인터럽트 뜸?  

one-shot mode라고해서
RID가 open되었다가 변경되어야 인터럽트가 뜨게 되어있음






### JIG연결했을때 바로 부팅하는이유?

PMIC는 두가지로 on할 수 있는데 1. power 키 2. JIGB(jig on) 신호 이다.
MUIC의 JIGB pin 이 PMIC에 연결되어있는데 PMIC에서 이부분을 인식하여 전원을 on시킴


- s2mu004 ctype + Factory mode

JIGB 신호 + VBATT 신호 있을때 pmic 에서 체크해서 부팅시킴? 

523K 연결시 JIGB low 이고 pmic 에서 이 신호 받음 -> 자동 부팅?
	factory mode 이기 때문에 system 전원은 VBATT 신호임

523K 제거할때 전원 꺼지는 이유? 
	FACtory mode 라서.

619K 연결시 JIGB low 안떨어진다고 하는데 바로 부팅하는 이유?


위 내용 다틀림 -> 부팅 자체는 JIGB를 보는게 아니라 ACOK pin을 보고 부팅한다.
619,523, TA모두 ACOK보고 PMIC에서 부팅시킴.


---------------

### FACTORY MODE ?

s2mu004 

공정바이너리 관련은 아니고 muic를 fatory mode로 사용한다는뜻은
폰내부에 load switch를 없애고 VBUS전원을(VBATT전원?) 시스템 전원으로 바로 사용한다는 뜻.
JIG 케이블이 연결되었을때(523K) JIG 전원(VBUS) 가지고 시스템 전원을 사용한다.
HW적으로 배터리에서 시스템으로 들어가는 전원이 차단됨.

- Factory mode 동작 

1. 523K JIG 가 삽입되면 자동으로(HW적으로) JIGB pin Low 
2. IFC_SENSE high
3. QBATENB high (L: 배터리 전원 VSYS로 사용, H: 배터리차단)
4. Charger에서 배터리 전원 차단시킴.
5. VBUS input pin인 (CHGIN) 에서 들어온 전원(input)이 VSYS (PMIC들어가는 전원) pin으로 나감(output) + VBAT 전원으로 나감

JIGB, QBATENB : B 로 끝나는 pin은 Active Low임


- Load Switch ?

JIG vbus전원을 시스템전원으로 사용할지 말지 선택할수 있는 스위치.

Load Switch가 있으면 위 동작 중 중간에 Load switch가 있어서 JIGB 가 low가 되었을때,
IFC_SENSE신호를 컨트롤해서 BATT전원을 차단 시킬지 사용할지 선택할 수 있다. 
Load switch가 따로 GPIO로 컨트롤 되어서 IFC_SENSE신호를 만들어줌.
(Grace과제 있음, A3/5/7 2017 과제에는 load switch 없음)

MUIC 에서 Fatory Mode를 사용한다는 의미는 Load Switch를 제거한다는 뜻이다.



- Factory mode 일때, 5V 전원을 줘야하는 이유.

s2mu004 charger가 default로 충전모드로 동작한다. VBATCHG (배터리 충전핀) 
Factory Mode일때 CHGIN으로 들어온 전원이 그대로 VBATCHG로 출력 됨.
배터리 전압보다 이 전압이 낮으면 배터리에 문제가 될 수 있기 때문에,
VBUS가 배터리 전압과 가까우면 VBUS를 차단시킴 (s2mu004만 해당되는건지는 확인필요)

VBUS 가 없으면 RID인식을 못해서 JIG cable 인식을 못함.
(로그상 부트로더에서 RID 0으로 출력됨.)
따라서 만약 4.2v 를 JIG전원으로 줬을때, VBUS가 차단되서 JIG cable인식이 안되서 UART통신도 안되고 그런것임.





## C type 관련





s2mu004


- 문제 : 케이블 연결 없이 부팅 완료 후 619K 삽입시 -> 인식 잘 안됌.
 원인 :
CC pin 연결되고 RID가 업데이트 되는데 200ms정도 걸림.
이게 업데이트 되기 전에 읽으면 619K jig 케이블 인식이 안됨.

```log
<6>[  101.528535]  [3:irq/3-s2mu004-u: 1106] [c3] usbpd-s2mu004 9-003c: s2mu004_set_normal_mode s2mu004 exit lpm mode
...
<6>[  101.694357]  [3:irq/3-s2mu004-u: 1106] [c3] usbpd-s2mu004 9-003c: s2mu004_pdic_check_rid : attached rid state(0)

```
위가 CC pin 연결이라고 보면됨
s2mu004_pdic_check_rid 에서 RID read 함. 200ms 이내에 읽어서 케이블 인식이 잘 안됐음.





### C type에서 RID 읽는 방법

기존 MUIC에서는 MUIC 에 연결되어있는 MUIC_ID pin 으로 adc저항 읽어서 케이블 구분

Ctype에서는 CC1 CC2의 저항 RD,RP 의 조합으로 인식함.

- C type 공정 관련
FOGO JIG (커넥터 말고 그냥 pin접촉으로 연결하는 jig pin ,smd array board에서 사용)
SMD 시 pba array download 상황에서는 비용절감?목적으로 C 커넉터 자체가 안달려있다.
그래서 CC pin이 있을 수 가 없다. 따라서 기존처럼 CCpin말고 MUIC_ID 로 읽어야함.




###  s2mu004 cable 인식 시퀀스 정리

```
 , adc:0x0, vbvolt:0x1, apple:0x6, chg_type:0x0, vmid:0x1, dev_id:0x28
          => 최초 부팅시 ADC값이 0으로 읽힘
 [c0] s2mu004_muic_detect_dev :[muic] change mode to second attach!
               =>  adc가 0으로 셋팅된것으로 보고 cable로 인식하고 RID disable
	       -> rid disable된 상황에서 301K detect인터럽트 발생하지 않음
						     
```

#### JIG 인식

#### 일반 TA 삽입 (Dedicate Charger Port)

#### 고속충전 TA 삽입 

#### 설삽

#### 물기 인식

#### USB 케이블 삽입시 (PC)

1. Interrupt (VBUS_ON) irq

```log
 s2mu004_irq_thread: muic interrupt(0x00, 0x01)
 s2mu004:s2mu004_muic_irq_thread muic mode (0) irq_num (29)
```

첫번째 인터럽트이므로 mode 는 NONE_CABLE
mode :	muic_data->attach_mode = S2MU004_NONE_CABLE;



2. s2mu004_muic_detect_dev 호출


3. first attach

```log
 s2mu004:s2mu004_muic_detect_dev
 s2mu004_muic_detect_dev :[muic] change mode to first attach!
```
first attach로 muic_pdic_notifier_attach_attached_dev 날림


4. second attacch

```log
 s2mu004_muic_detect_dev :[muic] change mode to second attach!
```
vbvolt 가 있었다면 바로 second attach뜸. -> 인터럽트가 뜨도록 설정하는듯?(RID disable)



5.  Interrupt (IRQ1_ATTATCH) irq

```log
 s2mu004_irq_thread: muic interrupt(0x01, 0x00)
 s2mu004:s2mu004_muic_irq_thread muic mode (2) irq_num (23)
```

코드상 vbvolt 있었으므로 Mode 는 SECOND_ATTACH
mode : static_data->attach_mode = S2MU004_SECOND_ATTACH;


6. s2mu004_muic_detect_dev 호출

 s2mu004:s2mu004_muic_detect_dev
SECOND_ATTACH 이므로 attach_mode 체크하는 코드 타지않고 바로 
device_type1 레지스터 읽어서 CDP, USB, SDP, TA  구분해서

7.  s2mu004_muic_handle_attach 호출
구분된 new_dev 에따라서 MUIC PATH 변경




참고 irq 번호

	S2MU004_MUIC_IRQ1_ATTATCH, //23
	S2MU004_MUIC_IRQ1_DETACH,
	S2MU004_MUIC_IRQ1_KP,
	S2MU004_MUIC_IRQ1_LKP,
	S2MU004_MUIC_IRQ1_LKR,
	S2MU004_MUIC_IRQ1_RID_CHG,

	S2MU004_MUIC_IRQ2_VBUS_ON, //29
	S2MU004_MUIC_IRQ2_RSVD_ATTACH,
	S2MU004_MUIC_IRQ2_ADC_CHANGE,
	S2MU004_MUIC_IRQ2_STUCK,
	S2MU004_MUIC_IRQ2_STUCKRCV,
	S2MU004_MUIC_IRQ2_MHDL,
	S2MU004_MUIC_IRQ2_AV_CHARGE,
	S2MU004_MUIC_IRQ2_VBUS_OFF, //36



#### JIG 케이블 삽입시 muic 인터럽트 순서

 s2mu004_irq_thread: muic interrupt(0x20, 0x01) -> second attach
 s2mu004_irq_thread: muic interrupt(0x02, 0x04) -> rid diable이후에 발생하는 인터럽트

 보통 이 지점에 ccic 인터럽트 발생 -> CCIC A
 1. muic_handle_ccic_notification: CCIC_NOTIFY_ID_ATTACH: Attached
 2. muic_handle_ccic_notification: CCIC_NOTIFY_ID_RID
 	

 s2mu004_irq_thread: muic interrupt(0x01, 0x00) -> 무시됨
 s2mu004_irq_thread: muic interrupt(0x00, 0x00)



### AFC


인터럽트가 여러번뜨는데 맨처음 DCP TA로 인식해서 afc prepare통신한뒤 AFC 인터럽트를 띄워줌.

맨처음 부팅중 probing 중? MUIC 에서 reset을 한뒤에 AFC인터럽트를 뜨게해서 이부분 체크.


AFC interrupt 크게 4가지
	S2MU004_AFC_IRQ_VbADC, (544)  -> V 전압이 바뀌었을때 irq ,
			 	MUIC에서 ADC 읽는 모드 : continue/oneshot mode 를 바꿈.
	S2MU004_AFC_IRQ_VDNMon, (545) -> D- 60K 저항 인식했을때, 즉 AFC 케이블 꽂혔을때
	S2MU004_AFC_IRQ_MPNack, (547) -> QC 2.0
	S2MU004_AFC_IRQ_MRxRdy, (551) -> slave ping 을 받았을때 뜨는 irq



SET ---master--> TA
SET <--slave---- TA

9V-5v toggle 함수 내용, (발열제어 목적)

1. TX data 생성?전송?
2. VbADC continue 모드변경 
3. Master ping  -> Voltage변경됨

그러면 voltage가 변경되었기 때문에 VbADC irq  받고
그리고 slave ping을 받았기 때문에 mrxrdy irq 둘다 받을 수 있음.?



9V AFC TA 케이블 연결 시 기본 동작순서

1. VDNMon 인터럽트
	D- 60K 연결된것을 확인해서 뜸.
	1. tx data 레지스터에 쓴뒤
	2. VbADC continue 로변경(그래야 AbADC 인터럽트를 받을 수 있음)
	3. tx데이터를 Master Ping 날림

2. VbADC 인터럽트 (s2mu004는 이 지점에서 발생안함)
	5V 로 중간에 한번 뜸. (발생 안하는 경우가 더 많음)
	그뒤 특별히 해야할일 없음
	state 머신 때문인듯?

3. MRxRdy 인터럽트 (x3 뜸)
	그 뒤 동일하게 
	1. tx data 레지스터에 쓴뒤
	2. VbADC continue 로변경(그래야 AbADC 인터럽트를 받을 수 있음)
	3. tx데이터를 Master Ping 날림
	
	AFC spec상 이동작을 3번 해야 실제 AFC TA에서 승압이 됨. (안정성 때문?)


4. AFC TA 에서 9V 로 승압됨

5. VbADC 인터럽트
	9V 승압 되었기 때문에 뜸.
	9V 케이블 재인식
	ATTACHED_DEV_AFC_CHARGER_9V_MUIC

6. muic_notifier 로 cable type 전송.
	ATTACHED_DEV_AFC_CHARGER_9V_MUIC



### AFC 인식 timming

① DCP 인식시 AFC 2s Timer 설정 

② 2s 이내에 DP-DM open 되면 AFC로 동작

③ 2s 이후(Timeout 발생 후) QC 동작 Retry

④ QC Fail 발생하면(고송충전하지 않으면) DCP 유지

 * AFC Spec에 2s는 없지만 2s로 사용하겠습니다.

  


### afc 관련 sysfs node


공정시나리오는 제가 알기로는 9V 인식 -> afc disable 후 5V 인식 -> 다음테스트

afc_disable 노드

[김지훈 / Ji-Hun Kim]
chg det re run 해서 5V인식하는거랑 muic_afc_set_voltage 이걸로 5V변경하는게 최종적으로는 똑같은것 아니에요?

[이희곤 / Heegon Lee] - 13:43                 
chg det re run 하면

[이희곤 / Heegon Lee] - 13:43                 
디태치노티가 한번날라가서

[이희곤 / Heegon Lee] - 13:43                 
충전아이콘 한번 깜빢 하거든요 ㅠ

[김지훈 / Ji-Hun Kim] - 13:44 
아 디태치가 한번 날라가는군요

[최인선 / insun choi] - 13:45                 
re-run 이면 chgtyp 을 다시 detect 하는거라서 이전 값이 빠질수 밖에 없으니 detach 로 가구요.

[최인선 / insun choi]
protocol 로 조정하는건 고속 충전 안에서 조정하는거라 detach 가 안갈듯.



공정앱 15모드 charge test 시나리오

```txt

[정욱현 / ukhyun jung] - 14:46                 
9V 충전기 꽂으면 5V 들어왔다가 9V 승압 되면
/sys/class/sec/switch/vbus_value 9V 읽구요
/sys/class/power_supply/battery/hv_charger_status 1로 승압 되었는지 읽구요
둘다 만족하면 
/sys/class/power_supply/battery/batt_current_ua_now 읽어서 5회 값 측정해서
SPEC IN 이면 PASS 하구요
이렇게 9V TEST 종료 되고.
9V TA 그대로 꽂혀진 상태에서 5V TEST 를 위해서
/sys/class/sec/switch/afc_disable 에 AFC_OFF write 해주구요.
똑같이 /sys/class/sec/switch/vbus_value 5v read 하고 
/sys/class/power_supply/battery/batt_current_ua_now 읽어서 5회 값 측정해서
SPEC IN 이면 PASS 합니다.

듀얼충전 지원하는 모델이면 "/sys/class/power_supply/battery/mode" 노드에 master / dual read 하는게 추가됩니다.
/sys/class/sec/switch/afc_disable 에 AFC_OFF write 가 1로 write 해주는거네요.
테스트 종료할때 
sys/class/sec/switch/afc_disable 다시 0 으로 write 해주고 끝냅니다.

afc_set_voltage 이런 노드도 시나리오에 있는지?

[정욱현 / ukhyun jung] - 15:06                 
grace 할때 12v -> 9v -> 5v 때문에 
/sys/class/sec/switch/afc_set_voltage 에 9V / 5V write 해줬었는데요
그전에 noble 이엿나요 9v 처음 들어올때.
그땐 필요없이 afc_disable 만 해도 5V로 떨어졌어요

```

### 공정 water int test
PD charge test 항목에 세번째 항목
muic id pin (수분감지용) 이 저항때문에 케이블이 삽입되면 adc 가 0으로 읽히고
케이블이 삽입되지 않으면 adc가 0x1F (OPEN) 으로 읽힘.
해당 테스트 항목은 이름과 다르게 수분감지 관련 테스트가 아니라,
케이블이 삽입되었을때 adc 가 0으로 출력되는지만 확인하는 테스트임.


### 공정바이너리에서 619K  삽입시 dock noti 떠서 wakeup시킴

공정바이너리에서 슬립진입했을떄, 
ATTACHED_DEV_JIG_UART_ON_MUIC 인식 시에 자동으로 깨어날 방법이없어서
dock noti 받으면 wake up 처리시킴

참고 : 619K + VB 면 충전인식 되서 깨움


### attach_mode 의 의미는?


### 수분 감지 매커니즘

ADC  one-shot mode 와 preodic mode 차이는?


ADC_ONESHOT 모드로 바꾸는 이유가 recheck_adc() 할 때 인터럽트 발생하지 않도록 하기 위함?

[박세종 / Michael Sejong Park] - 15:52                 
수분 모드시 ADC_ONESHOT 모드로 바꾸는 이유는 무선사 신뢰성에서 그렇게 하도록 가이드를 받았습니다,,

[박세종 / Michael Sejong Park]
grace에서 수분 상황에서 인터럽트가 과도하게 발생하는 경우를 방지하기 위함으로 알고있습니다,,




기존 grace과제

``````````````````````````````````````````````````````````c
"drivers/ccic/s2mu004-usbpd.c"
# void ccic_event_work(void *data, int dest, int id, int attach, int event)
| INIT_WORK(&event_work->ccic_work, ccic_event_notifier);
| queue_work(usbpd_data->ccic_wq, &event_work->ccic_work);

# static void ccic_event_notifier(struct work_struct *data)
| ccic_notifier_notify((CC_NOTI_TYPEDEF*)&ccic_noti, NULL, 0);

"drivers/ccic/ccic_notifier.c"
# int ccic_notifier_notify(CC_NOTI_TYPEDEF *p_noti, void *pd, int pdic_attach)
| switch (p_noti->id)
| | case CCIC_NOTIFY_ID_WATER:
| | | ccic_uevent_work(CCIC_NOTIFY_ID_WATER);

# static void ccic_uevent_work(int id)
| char *water[2] = { "CCIC=WATER", NULL };
| if (id == CCIC_NOTIFY_ID_WATER) {
| | kobject_uevent_env(&ccic_device->kobj, KOBJ_CHANGE, water);
   " 윗단에서 이 값을 받아서 처리"
``````````````````````````````````````````````````````````



### 설삽

설삽시 ATTACHED_DEV_TIMEOUT_OPEN_MUIC type으로 noti날려야함.
충전쪽에서 USB 전류로 충전함. 

그 후 완삽 시 ccic ATTACH noti가 오면 됨.

s2mu004에서 설삽 -> 몇분뒤 완삽시 케이블 재 인식하는 방법
````txt
1.    incompletion -> SDP_1P8S -> check flag (pmuic->is_dcdtmr_intr)
2.    completion -> CCIC ATTACH interrupt ->
2.    if flag set -> retry muic interrupt in order to try again whole cable detection process
````

- UI 컨셉

C-Type 케이블 설삽 상태에서는 1) 충전 인식음 / 진동 / 애니메이션 표시 안할 것 2) 화면 상단 배터리 번개 표시, 알림창에 충전 표시할 것

C-Type 케이블 완삽 상태에서는(설삽 후 완삽 or 바로 완삽) 1) 충전 인식음 / 진동 / 애니메이션 / 배터리 번개 / 알림창 충전 모두 표시할 것
	　
(Grace 과제 설삽 상태에서 충전 인식음 / 진동 / 애니메이션이 표시되어 정상 충전되는 것으로 오인식될 경우가 있어 컨셉을 변경함)


### UVLO
IFPMIC가 동작하는 입력전압 스레시홀드



### bypass mode 바이패스 모드


bypass는  들어가는 전원을 그대로 vsys로 넘겨주는것 charger에서 전류 측정시에 사용함.
그 전류 케이블 안에 DP DM이 숏 나있어서 DCP로 인식하는게 정상이라고 함.

```txt
전류측정 모드로 동작하는데 충전으로 인식했다는거 같은데 전류 케이블의 경우 APPLE chg로 인식할거 같은데 그게 문제가 되나 몰겠네요
[김지훈 / Ji-Hun Kim] - 17:46 로그상에는
[김지훈 / Ji-Hun Kim] - 17:46 [ 170.334430] [0:irq/7-s2mu004-i: 656] [c0] s2mu004_irq_thread: muic interrupt(0x01, 0x00) [ 170.337160] [0:irq/7-s2mu004-i: 656] [c0] s2mu004:s2mu004_muic_irq_thread muic mode (2) irq_num (23) [ 170.348652] [0:irq/7-s2mu004-i: 656] [c0] [muic] dev[1:0x40, 2:0x0, 3:0x0] [ 170.348652] [0:irq/7-s2mu004-i: 656] , adc:0x1f, vbvolt:0x1, apple:0x6, chg_type:0x1, vmid:0x1, dev_id:0x29 [ 170.348700] [0:irq/7-s2mu004-i: 656] [c0] s2mu004:s2mu004_muic_detect_dev [ 170.348735] [0:irq/7-s2mu004-i: 656] [c0] [muic] DEDICATED CHARGER DETECTED

[김지훈 / Ji-Hun Kim] - 17:46 DCP 로 인식됐네요

그 전류 케이블 안에 DP DM이 숏 나있어서 DCP로 인식하는게 정상이라고 합니다
```

참고메일 : FW: FW: [A520S] 슬립 전류 측정 시 충전 인식 확인 요청





### Role Swap

양쪽이 type-c 수컷인 케이블 양쪽에 폰 삽입 했을때, 한쪽으로 충전하게 해주는 기능
기존 power sharing 기능인데 (type-c용)
충전 방향 선택할 수 있도록 팝업이 뜸
