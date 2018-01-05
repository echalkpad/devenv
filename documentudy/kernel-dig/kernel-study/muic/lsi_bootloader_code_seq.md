### 기본 code 순서    
    
__/arch/arm/lib/init.c__       
# int start_sboot(void)       
| | mach_board_initialize,     
| | |	board_gpio_init();  
| | |	init_microusb_ic();      
| | mach_board_main,     
| | print_prompt,     
     
    
__/board/mach-joshua.c__      
    
# int mach_board_initialize(void)      
| | init_microusb_ic();      
| | | __/drivers/muic_s2mm001b.c__    
| | | | u32 init_microusb_ic(void)    
| | | | | MUIC 초기화    
| | | | | microusb_get_attached_device();    
| | | | | 이함수에서 각 디바이스에 현재 커넥터에대해 알려줌.(usb,charger,jig상태판단 등)      
| int mach_board_main(void)  
   
  
  
  
### Jig 상태(USB-ON/OFF UART-ON/OFF) 확인.    
    
  
```c  
# int start_sboot(void) "arch/arm/lib/init.c"  
| init_func_t **fptr = boot_sequence;  
| @ typedef int (init_func_t)(void);  
| @ static init_func_t *boot_sequence[] =   
| for (; *fptr; fptr++)  
|	mach_board_initialize();  
  
| # int mach_board_initialize(void)  
| 	mach_board_main();  
  
| # int mach_board_main(void)  
| 	print_prompt();  
  
| # static int print_prompt(void) "arch/arm/lib/init.c"  
| | if (!get_jig_status())  
| | @ u32 get_jig_status(void) __attribute__((weak, alias("__get_jig_status"))); "drivers/muic-core.c"  
| | # u32 __get_jig_status(void)  
| | | return pmuic->get_jig_status ? pmuic->get_jig_status() : 0;  
| | | @ pmuic->get_jig_status = s2mu005_get_jig_status; "drivers/muic_s2mu005.c"  
  
|   
  
```  
  
/arch/arm/lib/init.c  
> static int print_prompt(void)    
  
| static int print_prompt(void)  
>> 	if (!get_jig_status())    
>>>		__/drivers/muic_s2mm001b.c__    
>>>		u32 get_jig_status(void)    
>>>>			u32 device = microusb_get_attached_device();    
  
  
  
### Charger에 디바이스 타입 정보 제공    
__/drivers/muic_s2mm001b.c__    
u32 get_charger_status(void)  
>	int vbus = get_vbvolt();  
>>	VBUS있는지 레지스터 비트 확인(0x15)    
>	u32 device = microusb_get_attached_device();  
>최종 invalid 차쳐인지  valid차져 인지 리턴해줌.    
  
### high current cable 확인(charger에서 사용)    
__/drivers/muic_s2mm001b.c__    
u32 is_hc_cable(void)  
>	u32 device = microusb_get_attached_device();  
  
  
### USB cable인지 확인해줌.    
__/drivers/muic_s2mm001b.c__    
u32 is_usb_cable(void)  
>	u32 device = microusb_get_attached_device();  
>	S2MM001B_MUIC_USB (SDP), S2MM001B_MUIC_JIG_USB_ON, S2MM001B_MUIC_JIG_USB_OFF    
>	이면 true리턴    
  
### UART설정   
__/drivers/muic_s2mm001b.c__    
int set_muic_uart_early(void)  
  
  
### 부식방지 기능 enable    
__/board/mach-joshua.c__      
int mach_board_main(void)  
>	__/drivers/muic_s2mm001b.c__    
>	void enable_rustproof(void)  
  
### Download할때 adc값 확인     
__/drivers/s5p_download.c__  
int s5p_check_download(void)  
>		if (check_jig_adc_value(GD_JIG_STATUS_DOWNLOAD) == TRUE)   
>> 			__/drivers/muic_s2mm001b.c__    
>>>			int check_jig_adc_value(int mode)  
  
  
  
### Download할때 vbus out 설정    
static void prepare_download(void)  
	set_usb_vbus_out();  
>		__/drivers/muic_s2mm001b.c__    
>		int set_usb_vbus_out(void)  
  
  
### MUIC i2c용 GPIO 셋팅  
__/board/mach-joshua.c__      
int mach_board_initialize(void)      
>	board_gpio_init();  
>>		gpio_i2c[0][I2C_CH_MUIC] = GPIO_MUIC_SCL;  
>>		gpio_i2c[1][I2C_CH_MUIC] = GPIO_MUIC_SDA;  
  
  
### 기본통신은 i2c 사용 muic_s2mm001b.h에 함수 정의    
__/include/asm/arch-exynos/muic_s2mm001b.h__  
#define S2MM001B_I2C_CH				I2C_CH_MUIC  
#define S2MM001B_MUIC_WRITE(A,B)	ext_i2c_write(S2MM001B_I2C_CH, S2MM001B_I2C_ADDRESS, A, B)  
  
  
  
  
  
  
  
  
  
## boot param pmic_info 로 rust proof 어떻게 enable되는지? "joon"  
  
  
- boot param pmic_info 어디서 값 초기화?  
  
```c  
# static void setKernelParam(void) "lib/bootm.c"  
| pmic_info = cur_param_data_int(PARAM_SWITCH_SEL);  
| #if defined(CONFIG_USE_MUIC)  
| 	pmic_info |= (get_if_pmic_rev() << 4) | (check_rustproof(pmic_info) << 3);  
"check_rustproof(pmic_info) 의 값이 0x00이 되어야 부식방지 ON임"  
  
| # int check_rustproof(int sw_sel) "drivers/muic_core.c"  
| | int jig_rustproof = g_bd.rustproof_mode ^ 1;  
    " g_bd.rustproof_mode ==> 0x00 이면 ^ 0x01 하게되면 1이됨. (^ : 같으면0 다르면1) "  
| | int param_rustproof = (sw_sel >> 3) & 1;  
| | return jig_rustproof;  
  
| ptr += sprintf(ptr, " pmic_info=%d", pmic_info);  
  
```  
  
  
- g_bd.rustproof_mode 는 어디서 설정? "값이 1이 되어야함."  
  
```c  
  
# static void board_uart_rustproof(void) "board/mach-joon.c"  
| #if defined(CONFIG_BUILD_TYPE_USER) && !defined(CONFIG_SEC_FACTORY_BUILD)  
"CONFIG_BUILD_TYPE_USER true이어야 함 - 그러나 현재 이 config가 false임 -> user build가 되어야함?"  
| #if defined(CONFIG_MUIC_SUPPORT_RUSTPROOF)  
| int batt = battery_detect();  
| g_bd.rustproof_mode = 1; /* default */  
| if (batt)  
| 	g_bd.rustproof_mode = 0;  
  
```  
결국 USER 빌드된 바이너리에서만 rust proof모드 정상 동작하는지 확인 가능함.  
pbs에서 user build하면 CONFIG_BUILD_TYPE_USER 가 enable되는지 확인중.  
  
  
  
## 참고  __attribute__((weak, alias("__함수명"))); 에대하여    
  
```c  
  
/* in GCC manual */  
void __f () { /* Do something. */; }  
void f () __attribute__ ((weak, alias ("__f")));  
  
int __battery_detect(void)  
{  
	printf("[MUIC] couldn't find battery_detect api\n");  
  
	return 1;  
}  
  
int battery_detect(void)  
	__attribute__((weak, alias("__battery_detect")));  
```  
  
### 1. alias는 함수명을 바꿔줌.  
https://gcc.gnu.org/onlinedocs/gcc/Function-Attributes.html  
  
### 2 weak 옵션,   
기본적으로 동일한 함수이름이 같이 compile되면 컴파일에러남.  
weak attribute를 지정하면 동일한 이름을 가진 함수를 추가로 만들수 있음.  
(라이브러리 함수 원형을 정의 해줄때 많이 사용, 주로 함수내용은 비어있음)  
함수내용은 유져 파일에서 구현.  
http://www.valvers.com/programming/c/gcc-weak-function-attributes/  
  




## CONFIG_MUIC_FACTORY_MODE  

폰 내부에 load switch 없애고 VBAT 라인 없애서 vbus 만 가지고 동작하도록 만든 기능.
load switch : JIG 케이블이 연결 되었을때 VBAT VBUS shift 해주는 부품?
VBAT 라인 : 
