    
## 0. Initialization      
    
## 1. Cable 연결시      
    
```c      
s2mu005_muic_irq_thread(int irq, void *data)	"drivers/muic/s2mu005-muic.c"       
| s2mu005_muic_detect_dev(muic_data);      
| | s2mu005_muic_handle_attach(muic_data, new_dev, adc, vbvolt);      
| | | muic_notifier_detach_attached_dev(muic_data->attached_dev);	"drivers/muic/muic_notifier.c"      
| | | | muic_notifier_notify();      
| | vbus_notifier_handle((!!vbvolt) ? STATUS_VBUS_HIGH : STATUS_VBUS_LOW);      
    
```    
    
- Notifier 호출      
    
```c      
muic_notifier_notify();		"drivers/muic/muic_notifier.c"      
| blocking_notifier_call_chain(&(muic_notifier.notifier_call_chain),    
			muic_notifier.cmd, &(muic_notifier.attached_dev));    
| | " Calling Callback functions list "      
| | static int charger_handle_notification(struct notifier_block *nb,	"drivers/power/s2mu005_charger.c"    
| | static int batt_handle_notification(struct notifier_block *nb,	"drivers/battery/sec_battery.c"    
| | static int muic_handle_dock_notification(struct notifier_block *nb,	"drivers/muic/muic-core.c"    
| | static int usb_handle_notification(struct notifier_block *nb,	"drivers/usb/notify/usb_notifier.c"    
    
```      
    
- Muic 에 등록된 notifier 등록과정      
    
```c      
muic_notifier_register(&charger->cable_check, charger_handle_notification, 	"drivers/power/s2mu005_charger.c"    
muic_notifier_register(&battery->batt_nb, batt_handle_notification,	"drivers/battery/sec_battery.c"    
muic_notifier_register(&dock_notifier_block, muic_handle_dock_notification,	"drivers/muic/muic-core.c"    
muic_notifier_register(&pdata->usb_nb, usb_handle_notification, "drivers/usb/notify/usb_notifier.c"    
    
| int muic_notifier_register(struct notifier_block *nb, notifier_fn_t notifier,		"drivers/muic/muic_notifier.c"      
| | SET_MUIC_NOTIFIER_BLOCK(nb, notifier, listener);    
| | | #define SET_MUIC_NOTIFIER_BLOCK(nb, fn, dev) do 	\    
| | | 		(nb)->notifier_call = (fn);		\    
| | blocking_notifier_chain_register(&(muic_notifier.notifier_call_chain), nb);    
    
```      
    
    
    
- blocking_notifier_chain_register() 순서        
    
```c    
blocking_notifier_chain_register(&(muic_notifier.notifier_call_chain), nb); "drivers/muic/muic_notifier.c"    
int blocking_notifier_chain_register(struct blocking_notifier_head *nh, struct notifier_block *n) "kernel/notifier.c"      
| notifier_chain_register(&nh->head, n);    
    
    
```    
    
    
- blocking_notifier_call_chain() 순서    
    
```c    
blocking_notifier_call_chain(&(muic_notifier.notifier_call_chain),    
		muic_notifier.cmd, &(muic_notifier.attached_dev)); "drivers/muic/muic_notifier.c"    
| int blocking_notifier_call_chain(struct blocking_notifier_head *nh, unsigned long val, void *v)    
| | __blocking_notifier_call_chain(nh, val, v, -1, NULL);    
| | | notifier_call_chain(&nh->head, val, v, nr_to_call, nr_calls);    
| | | | while (nb && nr_to_call) {    
| | | | 	nb->notifier_call(nb, val, v);    
    
```    
  
}  
  
  
  
  
## 케이블 연결시 Interrupt 호출 순서.    
  
### 1. irq 등록     
  
```c    
+ static int s2mu005_i2c_probe(struct i2c_client *i2c,	"drivers/mfd/s2mu005_core.c"    
| | struct s2mu005_dev *s2mu005;  
| | s2mu005->irq = i2c->irq;  
| | pdata->irq_base = irq_alloc_descs(-1, 0, S2MU005_IRQ_NR, -1);  
| | s2mu005->irq_gpio = pdata->irq_gpio;  
| | ret = s2mu005_irq_init(s2mu005);  
| + int s2mu005_irq_init(struct s2mu005_dev *s2mu005)	"drivers/mfd/s2mu005_irq.c"  
| | | s2mu005->irq = gpio_to_irq(s2mu005->irq_gpio);	"gpio 23 번은 s2mu005 INT pin으로 등록함, irq 구조체에 gpio 인터럽트로 등록"  
| | | gpio_direction_input(s2mu005->irq_gpio);  
| | | ret = request_threaded_irq(s2mu005->irq, NULL, s2mu005_irq_thread, "s2mu005_irq_thread() 인터럽트 핸들러"  
				   IRQF_TRIGGER_LOW | IRQF_ONESHOT, "s2mu005-irq", s2mu005);  
| | + static irqreturn_t s2mu005_irq_thread(int irq, void *data)  
  
  
```  
  
  
### 2. 인터럽트 핸들러 calling    
  
```c  
+ static irqreturn_t s2mu005_irq_thread(int irq, void *data)	"drivers/mfd/s2mu005_irq.c"  
| ret = s2mu005_read_reg(s2mu005->i2c, S2MU005_REG_SC_INT, &irq_reg[CHG_INT]); "charger 인터럽트 레지스터 read"  
| ret = s2mu005_read_reg(s2mu005->i2c, S2MU005_REG_FLED_INT, &irq_reg[FLED_INT]); "flash led 인터럽트 레지스터 read"  
| ret = s2mu005_bulk_read(s2mu005->i2c, S2MU005_REG_MUIC_INT1,	"@@참고 1 : MUIC 인터럽트 레지스터 Read"  
				S2MU005_NUM_IRQ_MUIC_REGS, &irq_reg[MUIC_INT1]);  
| for (i = 0; i < S2MU005_IRQ_NR; i++)  
| 	handle_nested_irq(s2mu005->irq_base + i); "s2mu005->irq 에 등록된 핸들러 하나씩 호출하는듯?"  
  
```  
> @@참고 1 :  
>> s2mu005 muic int register 주소==> 04h, 05h 주요 bit  
>> (04h) [1]:dettach [0]:attach  
>> (05h) [7]:vbus off [2]:ADC changing [0]:vbus on  
  
  
  
  
+static int s2mu005_muic_probe(struct platform_device *pdev)	"drivers/muic/s2mu005-muic.c"  
| | ret = s2mu005_muic_irq_init(muic_data);  
| + static int s2mu005_muic_irq_init(struct s2mu005_muic_data *muic_data)  
| | | muic_data->irq_attach = irq_base + S2MU005_MUIC_IRQ1_ATTATCH; "irq_base는 s2mu005_core.c 에서 설정"  
| | | REQUEST_IRQ(muic_data->irq_attach, muic_data, "muic-attach");  
| | + #define REQUEST_IRQ(_irq, _dev_id, _name)				\  
	ret = request_threaded_irq(_irq, NULL, s2mu005_muic_irq_thread,	0, _name, _dev_id);  
	"s2mu005_muic_irq_thread()는 MUIC 의 인터럽트 핸들러"  
	"_irq 는 시스템에 약속된 해당 irq 번호인듯??"  
  
  
  
  
### request_threaded_irq 분석  
  
  
  
  
  
  
  
## 부식방지 기능 Rust proof   
  
- is_rustproof가 true일때 uart 차단되는 과정  
  
```c  
# static void s2mu005_muic_handle_attach(struct s2mu005_muic_data *muic_data, "drivers/muic/s2mu005-muic.c"  
| case ATTACHED_DEV_JIG_UART_OFF_MUIC:  
| ret = attach_jig_uart_boot_off(muic_data, new_dev);  
| # static int attach_jig_uart_boot_off(struct s2mu005_muic_data *muic_data,  
| | ret = switch_to_ap_uart(muic_data);  
| | # static int switch_to_ap_uart(struct s2mu005_muic_data *muic_data)  
| | | ret = com_to_uart(muic_data);  
| | | # static int com_to_uart(struct s2mu005_muic_data *muic_data)  
| | | | if (muic_data->is_rustproof)  
| | | | 	return ret; "아래 코드를 진행하지 않고(uart enable X) return"  
| | | | reg_val = MANSW_UART;  
| | | | ret = set_com_sw(muic_data, reg_val);  
  
```  
  
> 참고 uart enable 관련 reg    
```c    
MANSW_UART		=	(MANUAL_SW_UART | MANUAL_SW_CHARGER),  
| #define MANUAL_SW_UART		(0x2 << MANUAL_SW_DM_SHIFT | 0x2 << MANUAL_SW_DP_SHIFT)  
| | #define MANUAL_SW_DM_SHIFT		5  
| | #define MANUAL_SW_DP_SHIFT		2  
| #define MANUAL_SW_CHARGER	(0x1 << MANUAL_SW_CHG_SHIFT)  
| | #define MANUAL_SW_CHG_SHIFT		1  
"최종 MANSW_UART => 0b 0100 1010"  
"MUIC Control Register (0xB5h)  from S2MU005  
dM_SWITCHING[7:5] (010): UTX1 is connetected to DM  
DP_SWITCHING[4:2] (010): UTX1 is connetected to DP  
RSVD[1] (1) :reserved "  
```  
  
  
- muic_data->is_rustproof 는 어떻게 설정?  
  
```c  
  
# static int s2mu005_muic_probe(struct platform_device *pdev) "drivers/muic/s2mu005-muic.c"  
| ret = muic_data->pdata->init_gpio_cb(get_switch_sel());  
  
| # int get_switch_sel(void) "drivers/muic/muic-core.c"  
| | return muic_pdata.switch_sel;  
  
| | @ static int set_switch_sel(char *str) "참고: switch_sel 은 Boot param으로 넘어옴"  
| | | muic_pdata.switch_sel = (muic_pdata.switch_sel) & 0xfff;  
| | | return muic_pdata.switch_sel; "muic_pdata.switch_sel ==> 0x5b "  
| | | __setup("pmic_info=", set_switch_sel);  
  
| @ .init_gpio_cb	= muic_init_gpio_cb, "drivers/muic/muic-core.c"  
| # static int muic_init_gpio_cb(int switch_sel)  
| | #if defined(CONFIG_MUIC_RUSTPROOF_ON_USER) && !defined(CONFIG_SEC_FACTORY)  
| | if (!(switch_sel & SWITCH_SEL_RUSTPROOF_MASK))  
| | 	pdata->rustproof_on = true;  
| | " SWITCH_SEL_RUSTPROOF_MASK	= 0x8,"  
  
| muic_data->is_rustproof = muic_data->pdata->rustproof_on;  
  
```  
