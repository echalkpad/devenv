


### 각종 케이블 정상인식

부팅 이후
USB, TA, AFC cable삽입시 cable type 인식 및 충전마크

USB, TA, AFC cable삽입 하고 재부팅시 정상 인식


notifier 정상적으로 전달되는지확인

### PATH변경
JIG UART삽입시 uart path 연결
	AT cmd 동작 또는 uart log

PC와 USB연결시 usb path 연결

### JIG관련

sleep이후 619K (no VB) 삽입 되었을때 wake-up되어야함.
(공정바이너리에서 -> dock noti사용함)

### 공정 관련

AT+OTGG_TEST

### sysfs 노드 관련


#*0*# 진입시 /sys/class/sec/switch/uart_en 1 write되어 uart path연결되야함


### C-type 관련

FACTORY mode인 경우 확인사항



