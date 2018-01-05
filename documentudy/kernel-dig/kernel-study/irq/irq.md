
## request_threaded_irq 분석

1. 인터럽트 등록

```c
# int s2mu005_irq_init(struct s2mu005_dev *s2mu005) "drivers/mfd/s2mu005_irq.c"
| s2mu005->irq = gpio_to_irq(s2mu005->irq_gpio); 
      "s2mu005->irq_gpio ==> 3이고 return 값으로 7로 등록되는데 무슨값인지?"
	" 참고 dts s2mu005,irq-gpio = <&gpa2 7 0>;"
| # static inline int gpio_to_irq(unsigned int gpio) "include/linux/gpio.h"
| | return __gpio_to_irq(gpio);
| | # static inline int __gpio_to_irq(unsigned gpio) "include/asm-generic/gpio.h"
| | | return gpiod_to_irq(gpio_to_desc(gpio));
| | | # struct gpio_desc *gpio_to_desc(unsigned gpio)
| | | | return &gpio_desc[gpio];
| | | # int gpiod_to_irq(const struct gpio_desc *desc) "drivers/gpio/gpiolib.c"
| | | | struct gpio_chip *chip;
| | | | chip = desc->chip;
| | | | offset = gpio_chip_hwgpio(desc);
| | | | # static int __maybe_unused gpio_chip_hwgpio(const struct gpio_desc *desc)
| | | | | return desc - &desc->chip->desc[0];
| | | | return chip->to_irq ? chip->to_irq(chip, offset) : -ENXIO;
| | | | @ .to_irq = samsung_gpio_to_irq, "drivers/pinctrl/samsung/pinctrl-samsung.c"
| | | | # static int samsung_gpio_to_irq(struct gpio_chip *gc, unsigned offset)
| | | | | struct samsung_pin_bank *bank = gc_to_pin_bank(gc);
| | | | | # static inline struct samsung_pin_bank *gc_to_pin_bank(struct gpio_chip *gc)
| | | | | | return container_of(gc, struct samsung_pin_bank, gpio_chip);
| | | | | virq = irq_create_mapping(bank->irq_domain, offset);
| | | | | # unsigned int irq_create_mapping(struct irq_domain *domain, "kernel/irq/irqdomain.c"
				irq_hw_number_t hwirq)
| | | | | return (virq) ? : -ENXIO;

| ret = request_threaded_irq(s2mu005->irq, NULL, s2mu005_irq_thread,
				   IRQF_TRIGGER_LOW | IRQF_ONESHOT,
				   "s2mu005-irq", s2mu005);
```

"drivers/pinctrl/samsung/pinctrl-exynos.c"
"drivers/pinctrl/samsung/pinctrl-samsung.h"


2. 핸들러 호출

```c
static irqreturn_t s2mu005_irq_thread(int irq, void *data)
	/* Report */
	for (i = 0; i < S2MU005_IRQ_NR; i++) {
		if (irq_reg[s2mu005_irqs[i].group] & s2mu005_irqs[i].mask)
			handle_nested_irq(s2mu005->irq_base + i);
	}
```


## GPIO pinctrl 등록

+static int samsung_pinctrl_probe(struct platform_device *pdev)	"drivers/pinctrl/samsung/pinctrl-samsung.c"
| | ret = samsung_gpiolib_register(pdev, drvdata);
| | # static int samsung_gpiolib_register(struct platform_device *pdev,
				    struct samsung_pinctrl_drv_data *drvdata)
| | | bank->gpio_chip = samsung_gpiolib_chip;
| | | gc = &bank->gpio_chip;
| | | ret = gpiochip_add(gc); "gpio 등록 함수?"
| | | # int gpiochip_add(struct gpio_chip *chip) "drivers/gpio/gpiolib.c"
| | | | status = gpiochip_add_to_list(chip);



> 참고 
```c
static const struct gpio_chip samsung_gpiolib_chip = {
	.request = samsung_gpio_request,
	.free = samsung_gpio_free,
	.set = samsung_gpio_set_value,
	.get = samsung_gpio_get,
	.direction_input = samsung_gpio_direction_input,
	.direction_output = samsung_gpio_direction_output,
	.to_irq = samsung_gpio_to_irq,
	.owner = THIS_MODULE,
};
```




##  s2mu005 muic 인터럽트 핀은 어떻게 연결되고 초기화 하는가? (Joon과제)  

dts 파일에 인터럽트핀 등록하는 방법은?  

- SoC dtsi 파일
"exynos7880.dtsi"

```c

/include/ "exynos7880-pinctrl.dtsi"
...

	pinctrl_0: pinctrl@139F0000 {
		compatible = "samsung,exynos7880-pinctrl";
		reg = <0x0 0x139F0000 0x1000>;
		clocks = <&clock 154>;
		clock-names = "gate_pinctrl";
		wakeup-interrupt-controller {
			compatible = "samsung,exynos4210-wakeup-eint";
			interrupt-parent = <&gic>;
			interrupts = <0 16 0>;
			samsung,eint-flt-conf;
		};
	};
```

```c 
"exynos7880-pinctrl.dtsi"
	pinctrl@139F0000 {
		...
		gpa2: gpa2 {
			gpio-controller;
			#gpio-cells = <2>;

			interrupt-controller;
			#interrupt-cells = <2>;
		};
		...
	}
``` 

- board dts파일

```c 
"exynos7880-universal7880.dts"
s2mu005@3d {
	compatible = "samsung,s2mu005mfd";
	reg = <0x3d>;
	pinctrl-names = "default";
	pinctrl-0 = <&if_irq &if_pmic_rstb>;
	s2mu005,irq-gpio = <&gpa2 7 0>;
	s2mu005,wakeup;
}
```

회로도 확인시
XEINT_23 에 if_pmic_int가 연결되어 있음.

exynos7880 datasheet :
XEINT_23 | GPA2[7]/ ALV_DBG[23] |  로 되어있음.

따라서 dts파일에 "s2mu005,irq-gpio = <&gpa2 7 0>;" 라고 작성하면 됨.

GPA[3:0] (gpa0 ~ gpa3까지) 는 external wake up interrupt임

데이터 시트에서 gpa2_7 검색 하기


- java exynos 7570 경우

회로도 확인시 muic int pin이 xeint_9번으로 연결되어 있음.
exynos 7570 데이터시트 에서 xeint_9 검색
exint_9의 function은 gpa1 [1] 로 검색됨

따라서 dts파일에 "sm5504,irq-gpio = <&gpa1 1 0>; " 라고 작성하면 됨.




---------
of_get_named_gpio 분석


```c
muic_data->pdata->irq_gpio = of_get_named_gpio(np_muic, "rt8973,irq-gpio", 0);
```
muic_data->pdata->irq_gpio ==> 19 로 출력되는데 왜?

```c
	muic-rt8973@14 {
		...
		rt8973,irq-gpio = <&gpa1 1 0>;
	};
```


```c
# static int of_rt8973_muic_dt(struct device *dev, struct rt8973_muic_data *muic_data) "drivers/muic/rt8973.c"
| muic_data->pdata->irq_gpio = of_get_named_gpio(np_muic, "rt8973,irq-gpio", 0);
| # static inline int of_get_named_gpio(struct device_node *np, const char *propname, int index) "include/linux/of_gpio.h"
| | return of_get_named_gpio_flags(np, propname, index, NULL);
| | # int of_get_named_gpio_flags(struct device_node *np, const char *list_name, "drivers/gpio/gpiolib-of.c"
| | | struct gpio_desc *desc;
| | | desc = of_get_named_gpiod_flags(np, list_name, index, flags);
| | | # struct gpio_desc *of_get_named_gpiod_flags(struct device_node *np, "drivers/gpio/gpiolib-of.c"
		     const char *propname, int index, enum of_gpio_flags *flags)
	/* TODO */
| | | return desc_to_gpio(desc);
| | | # int desc_to_gpio(const struct gpio_desc *desc)
| | | | return desc - &gpio_desc[0];

```


## request_threaded_irq() 사용해 irq등록하는 방법


http://lwn.net/Articles/302043/






## irq domain이란?
Hardware interrupt 번호를 변경하는것과 연관이 있는듯.
참고 구조체

```c
 /* struct irq_domain - Hardware interrupt number translation object ..*/
struct irq_domain {
	...}
```

```c
# static int __init mt_eint_init(void)
| struct irq_domain *domain;
| domain = irq_domain_add_legacy(node, EINT_MAX_CHANNEL, EINT_IRQ_BASE, 0,
				       &mt_eint_domain_simple_ops, NULL);
...

"참고로 irq_domain_add_legacy함수는 결국 radix-tree사용."
# struct irq_domain *__irq_domain_add(struct device_node *of_node, int size,
| struct irq_domain *domain;
| INIT_RADIX_TREE(&domain->revmap_tree, GFP_KERNEL);

```





#### irq_set_irq_wake WARN 로그 발생 원인 분석과 해결.
과제 : mediatek, MT6755, MUIC(s2mu005)

1. Log

```log
[  123.900044] <1>-(4)[   system_server:1019] WARNING: CPU: 4 PID: 1019 at
/home/dpi/qb5_8814/workspace/MT6755/android/kernel/kernel/irq/manage.c:546 irq_set_irq_wake+0xc8/0xf8()
[  123.900051] <1>-(4)[   system_server:1019] Unbalanced IRQ 296 wake disable
```


2. 발생 코드 관련 분석

```c

# static int s2mu005_resume(struct device *dev) "drivers/mfd/s2mu005_core.c"
| struct s2mu005_dev *s2mu005 = i2c_get_clientdata(i2c);
| if (device_may_wakeup(dev))
|     disable_irq_wake(s2mu005->irq);
|--- 
| # static inline int disable_irq_wake(unsigned int irq) "include/linux/interrupt.h"
| | return irq_set_irq_wake(irq, 0);
| |--- 
| | # int irq_set_irq_wake(unsigned int irq, unsigned int on) "kernel/irq/manage.c"
| | | struct irq_desc *desc = irq_get_desc_buslock(irq, &flags, IRQ_GET_DESC_CHECK_GLOBAL);
| | | if (on) {
| | | } else {
| | |     if (desc->wake_depth == 0) {
| | |         WARN(1, "Unbalanced IRQ %d wake disable\n", irq); "문제 로그 발생지점"
| | |     } else if (--desc->wake_depth == 0) {
| | |         ret = set_irq_wake_real(irq, on); //}
| | |--- 
| | | # static int set_irq_wake_real(unsigned int irq, unsigned int on) "kernel/irq/manage.c"
| | | | ret = desc->irq_data.chip->irq_set_wake(&desc->irq_data, on);
| | | |--- 
| | | | @ static struct irq_chip mt_irq_eint = { "drivers/irqchip/irq-mt-eic.c"
| | | | | .name = "mt-eint",
| | | | | .irq_mask = mt_eint_irq_mask,
| | | | | .irq_unmask = mt_eint_irq_unmask,
| | | | | .irq_ack = mt_eint_irq_ack,
| | | | | .irq_set_type = mt_eint_irq_set_type, //}
| | | | | "irq_set_wake 콜백이 등록이 안되어 있어서 발생하는 문제"
| | | |--- 
| | | | | "아래의 irq_set_wake 함수를 참조하는 것이 아님!"
| | | | @ static struct irq_chip mtk_pinctrl_irq_chip = { "drivers/pinctrl/mediatek/pinctrl-mtk-common.c"
| | | | | .irq_set_wake = mtk_eint_irq_set_wake, //}
| | | | # static int mtk_eint_irq_set_wake(struct irq_data *d, unsigned int on)
| | | | | struct mtk_pinctrl *pctl = irq_data_get_irq_chip_data(d);
| | | | | if (on)
| | | | |     pctl->wake_mask[reg] |= BIT(shift);
| | | | | else
| | | | |     pctl->wake_mask[reg] &= ~BIT(shift);
| | |--- 
| | | if (ret)
| | | 	desc->wake_depth = 1;
| | | 	else
| | | 	irqd_clear(&desc->irq_data, IRQD_WAKEUP_STATE);


```


참고하기
Documentation/power/suspend-and-interrupts.txt




궁금점:
1. irq_desc 구조체는 어떤 역할, 어떤 내용이 담겨있나?
struct irq_desc (interrupt decriptor) 는 인터럽트 number마다 하나씩 가지고 있음.
2. desc->wake_depth 의 의미,
3. irq disable시에 wake_depth 변수가 왜 0이면 문제인가?


현재 문제는  irq_chip 구조체가 여러개 있는데 s2mu005에서 호출하는 구조체의
irq_set_wake 콜백함수가 없다는것임.
현재 eintc 의 구조체로 연결되어있는데 여기 irq_set_wake 콜백함수가 없음
pinctrl에는 irq_set_wake 콜백함수가 존재함.
그렇다면 interrupt 연결을 

eintc말고 drivers/pinctrl/mediatek/pinctrl-mtk-common.c 로 등록할 수 있는가?
eintc -> drivers/irqchip/irq-mt-eic.c

문제 하나는 JOON의 gp2?는 interrupt-controller인데 pio는 아님..

JOON			s2mu005,irq-gpio = <&gpa2 7 0>;
MTK			s2mu005,irq-gpio = <&pio 8 0>;

-> &pio interrupt-controller를 추가하면 어떻게됌?


- dtsi 에 
interrupt-controller 는 어떤 역할을 하나?

dts의 interrupt-controller 는 어떤 기능 함수에서 파싱해서 처리하나?



문제:  pio에 아래와같이  interrupt-controller 를 추가했더니

```dts
		pio: pinctrl@10005000 {
			...
			#interrupt-cells = <2>;
			interrupt-controller;
		};
```

아래에서 irq_of_parse_and_map 정상 수행을 못함 왜?

```c
# int mtk_pctrl_init(struct platform_device *pdev, "drivers/pinctrl/mediatek/pinctrl-mtk-common.c"
| irq = irq_of_parse_and_map(np, 0);
| if (!irq) {
| 	dev_err(&pdev->dev, "couldn't parse and map irq\n"); //}

```


- 먼저 irq_of_parse_and_map 분석

여기서 irq번호가 생성되는듯?
참고 꼭 읽기 http://egloos.zum.com/furmuwon/v/11004041

```c
# unsigned int irq_of_parse_and_map(struct device_node *dev, int index) "drivers/of/irq.c"
| struct of_phandle_args oirq;
| if (of_irq_parse_one(dev, index, &oirq))
|---
| # int of_irq_parse_one(struct device_node *device, int index, struct of_phandle_args *out_irq)
| | "전달받은 노드에서 각종 인터럽트 관련 property 파싱하는 함수"
| | addr = of_get_property(device, "reg", NULL);
| | res = of_parse_phandle_with_args(device, "interrupts-extended",
| | intspec = of_get_property(device, "interrupts", &intlen);
| | if (intspec == NULL)
| | 	return -EINVAL; "interrupts 프로퍼티가 없어서 return됨"
| | p = of_irq_find_parent(device);
| | tmp = of_get_property(p, "#interrupt-cells", NULL);
|---
| 	return 0;
| return irq_create_of_mapping(&oirq);
```

pio에 아래와같은 방식으로 해당 gpio pin에 대한 interrupts 프로퍼티 추가 하면?
```dts
	interrupts = <GIC_SPI 84 IRQ_TYPE_LEVEL_LOW>;
```
의문: 두번째 84값은 어떻게 정해지는 거임?
-> 84 + 32 한 값이 kernel에서 인터럽트 번호가 됨.
(GIC_SPI 일때는 32, 다른거일때는 16임)

```sh
root@mtkltectc:/ # cat proc/interrupts                                         
           CPU0       CPU4       CPU5       CPU6       CPU7       
 29:          0          0          0          0          0       GIC  29 arch_timer
 30:       3041       9536       7908       5440       3506       GIC  30 arch_timer
 96:          0          0          0          0          0       GIC  96 mtk_cpuxgpt0
..........
116:         35        153        230        172        123       GIC 116 11007000.i2c
```





### suspend시에 enable_irq_wake 를  사용하는 목적은?
deep sleep 상태에서도 wake할 수 있도록 대기하는것


Marvell, SM5504 MUIC 코드에서는 아래처럼 `IRQF_NO_SUSPEND` flag가 있기 때문에
suspend에서도 sleep에 빠지지 않는다.
(참고 : Documentation/power/suspend-and-interrupts.txt)
```c
	ret = request_irq(usbsw->irq, microusb_irq_handler,
			IRQF_NO_SUSPEND | IRQF_TRIGGER_FALLING,
			"sm5504 micro USB", usbsw);
```

하지만 S.LSI와 MTK에서 S2MU005_MUIC는 아래처럼 IRQF_NO_SUSPEND 가 없기 때문에,
suspend 에서 enable_irq_wake()로 sleep상태에서 irq를 받도록 설정 해야하고
rusume 에서 disable_irq_wake()로 위내용이 필요없으니 원상복구 해야한다.

```c
	ret = request_threaded_irq(s2mu005->irq, NULL, s2mu005_irq_thread,
				IRQF_TRIGGER_LOW | IRQF_ONESHOT,
				"s2mu005-irq", s2mu005);
```

```c
# static int s2mu005_suspend(struct device *dev)
| if (device_may_wakeup(dev))
| 	enable_irq_wake(s2mu005->irq);
| disable_irq(s2mu005->irq);

static int s2mu005_resume(struct device *dev)
| if (device_may_wakeup(dev))
| 	disable_irq_wake(s2mu005->irq);
| enable_irq(s2mu005->irq);
```
> (실험 1)
> requst irq함수에서 IRQF_NO_SUSPEND flag를 안준 s2mu005 경우
> suspend에서 enable_irq_wake를 주석처리하고 테스트 해보니, suspend진입 이후
> 실제로 케이블삽입해도 인터럽트 안뜸.
> -> 반면 MTK 과제에서는 enable_irq_wake 없이도 SPM driver가 deep sleep 으로부터 wake up을 시켜줌.
> -> 아래 SPM관련 코드 분석 참고
> (실험 2)
> IRQF_NO_SUSPEND 주고
> suspend에서 enable_irq_wake를 주석처리하고 테스트 해보니, suspend진입 이후
> 케이블 삽입시 인터럽트 -> 인터럽트 잘 뜰줄 알았는데 무한정 인터럽트가 뜸 (잘안됨)

> 추가
> (의문) : suspend에서 enable_irq_wake() 이후에 disable_irq() 를 하면 안되는것 아닌가?
> (의문) :  disable_irq() 를 하면 어떤게 달라지는지?, 실제로 동시에 사용하는 코드 발견됨.




- wakeup source 를 설정하기 위해 
irq_set_irq_wake() 콜백을 사용하는게 현재 MTK는 이 기능을 사용하지 않음.



### disable_irq 코드 분석

```c
# void disable_irq(unsigned int irq)
| if (!__disable_irq_nosync(irq))
| # static int __disable_irq_nosync(unsigned int irq)
| | __disable_irq(desc, irq);
| synchronize_irq(irq);
```
> 아래 suspend때와 마찬가지로 __disable_irq 가 호출됨
> IRQF_NO_SUSPEND 가 있으면 suspend시에 __disable_irq가 호출 안됨
> 따라서 IRQF_NO_SUSPEND 가 없다면 suspend시에 __disable_irq가 호출될 것이므로
> s2mu005_suspend() 에서 추가로 disable_irq() 해줄 필요 없는듯



### IRQF_NO_SUSPEND 플래그는 어떻게 사용되는가?

- suspend

```c
"/sys/power/state 를 통해 state_store() 가 호출되고
여러단계를 거쳐 아래 suspend_enter 까지 실행됨."
"중략..."
# static int suspend_enter(suspend_state_t state, bool *wakeup) "kernel/power/suspend.c"
| error = dpm_suspend_noirq(PMSG_SUSPEND);
| # int dpm_suspend_noirq(pm_message_t state) "drivers/base/power/main.c"
| | suspend_device_irqs();
| | # void suspend_device_irqs(void) "kernel/irq/pm.c"
| | | "/* suspend_device_irqs - disable all currently enabled interrupt lines */"
| | | for_each_irq_desc(irq, desc)
| | | | sync = suspend_device_irq(desc, irq);
| | | | # static bool suspend_device_irq(struct irq_desc *desc, int irq) "kernel/irq/pm.c"
| | | | | if (!desc->action || desc->no_suspend_depth)
| | | | | | return false; "no_suspend_depth 값이 true이면 아래 disable_irq실행 안됨"
| | | | | __disable_irq(desc, irq);

```

- free_irq()

각 드라이버에 재량으로 remove 호출시 free_irq 호출됨(suspend때마다 호출되지 않음)

```c
# void free_irq(unsigned int irq, void *dev_id) "kernel/irq/manage.c"
| kfree(__free_irq(irq, dev_id));
| # static struct irqaction *__free_irq(unsigned int irq, void *dev_id)
| | irq_pm_remove_action(desc, action);
| | # void irq_pm_remove_action(struct irq_desc *desc, struct irqaction *action) "kernel/irq/pm.c"
| | | if (action->flags & IRQF_NO_SUSPEND)
| | | | desc->no_suspend_depth--;
```

- __setup_irq()

```c
# int request_threaded_irq(unsigned int irq, irq_handler_t handler, "kernel/irq/manage.c"
| retval = __setup_irq(irq, desc, action);
| # __setup_irq(unsigned int irq, struct irq_desc *desc, struct irqaction *new)
| | irq_pm_install_action(desc, new);
| | # void irq_pm_install_action(struct irq_desc *desc, struct irqaction *action)"kernel/irq/manage.c"
| | | if (action->flags & IRQF_NO_SUSPEND)
| | | | desc->no_suspend_depth++;

```








### wake up source 란?



#### 참고 API

__pm_stay_awake()
> sleep 진입 막는것
wakeup_source_init()

enable_irq_wake()
> sleep진입해도 irq로 wake 가능하게 함.
> kernel core arch설정은 아닌것같고, AP reg설정으로 AP HW기능을 바로 설정하는 듯함.
> (desc->irq_data.chip->irq_set_wake 콜백 호출)

#### mt_irq_unmask_for_sleep 분석

```c
"mt_irq_unmask_for_sleep: enable an interrupt for the sleep manager's use"
# void mt_irq_unmask_for_sleep(unsigned int irq) "drivers/irqchip/irq-mt-gic.c"
| dist_base = gic_data_dist_base(&gic_data[0]);
| *(volatile u32 *)(dist_base + GIC_DIST_ENABLE_SET + irq / 32 * 4) = mask;
```
> sleep시 interrupt를 enable할 irq를 직접 IRQ 번호이용해 AP 레지스터 단에서 설정하는듯.
> 그런데 SPM_IRQ0_ID spm 용 irq번호만 이함수를 사용함..다른게 더있을듯


(의문) 아래 명령어 쳤을때 wakeup source로 나오는 방법?

#### MTK과제 : SPM드라이버 wakeup source 관련 찾아보기

- MTK에서 실제 wakeup 될때 호출되는 함수 분석

- 케이블 연결시 s2mu005 eint에 의해서 깨어나는 log 

```log
[  146.288518] <0> (0)[   system_server:1015] [SPM] wake up by R12_EINT_EVENT_B, timer_out = 473485, r13 = 0x6040000, debug_flag = 0x11fff
```


- __spm_output_wake_reason

```c

# static noinline void __init_refok rest_init(void)
| cpu_startup_entry(CPUHP_ONLINE);
| # void cpu_startup_entry(enum cpuhp_state state) "kernel/sched/idle.c"
| | cpu_idle_loop();
---
# static void cpu_idle_loop(void) "kernel/sched/idle.c"
| cpuidle_idle_call();
| # static void cpuidle_idle_call(void) "kernel/sched/idle.c"
| | entered_state = cpuidle_enter(drv, dev, next_state);
| | # int cpuidle_enter(struct cpuidle_driver *drv, struct cpuidle_device *dev, "drivers/cpuidle/cpuidle.c"
| | | return cpuidle_enter_state(dev, drv, index);
| | | # int cpuidle_enter_state(struct cpuidle_device *dev, struct cpuidle_driver *drv,
| | | | struct cpuidle_state *target_state = &drv->states[index];
| | | | entered_state = target_state->enter(dev, drv, index);
"그런데 이건 부팅할때라서, sleep이후 호출되는 것은 다시 분석필요"

@ static struct cpuidle_driver mt67xx_v2_cpuidle_driver = {
| .name             = "mt67xx_v2_cpuidle",
| .states[0] = {
| 	.enter            = mt_dpidle_enter,
| ...}

# static int mt_dpidle_enter(struct cpuidle_device *dev, "drivers/cpuidle/cpuidle-mt67xx_v2.c"
			      struct cpuidle_driver *drv, int index)
| return dpidle_enter(smp_processor_id());
| # int dpidle_enter(int cpu) "/drivers/misc/mediatek/base/power/spm_v2/mt_idle.c"
| | spm_go_to_dpidle(slp_spm_deepidle_flags, (u32)cpu, dpidle_dump_log);
| | # wake_reason_t spm_go_to_dpidle(u32 spm_flags, u32 spm_data, u32 dump_log)
```
> "그런데 이건 부팅할때라서, sleep이후 호출되는 것이 아님"


실제는 아래처럼 호출됨

```c

# int pm_suspend(suspend_state_t state)
| error = enter_state(state);
| # static int enter_state(suspend_state_t state)
| | error = suspend_devices_and_enter(state);
| | # int suspend_devices_and_enter(suspend_state_t state)
| | | do {
| | | | error = suspend_enter(state, &wakeup);
| | | } while (!error && !wakeup && platform_suspend_again(state));
| | | @ static const struct platform_suspend_ops *suspend_ops;
| | | # static int suspend_enter(suspend_state_t state, bool *wakeup)
| | | | error = suspend_ops->enter(state);

"drivers/misc/mediatek/base/power/spm_v2/mt_sleep.c"
@ static const struct platform_suspend_ops slp_suspend_ops = {
| .enter = slp_suspend_ops_enter,
| ...}
| "platform_suspend_ops 구조체는 BSP에서 만들어서 등록해야할 구조체임"
| "참고로 exynos는 drivers/soc/samsung/exynos-pm.c 에서 등록"

---
 "drivers/misc/mediatek/base/power/spm_v2/mt_sleep.c"
# static int slp_suspend_ops_enter(suspend_state_t state)
| slp_wake_reason = spm_go_to_sleep(slp_spm_flags, slp_spm_data);
| # wake_reason_t spm_go_to_sleep(u32 spm_flags, u32 spm_data)
| | last_wr = spm_output_wake_reason(&spm_wakesta, pcmdesc, vcore_status);
| | # static wake_reason_t spm_output_wake_reason(struct wake_status *wakesta, struct pcm_desc *pcmdesc, int vcore_status)
| | | wr = spm_output_wake_reason(&wakesta, pcmdesc, dump_log);
| | | # static wake_reason_t spm_output_wake_reason(struct wake_status *wakesta, struct pcm_desc *pcmdesc, u32 dump_log) "drivers/misc/mediatek/base/power/spm_v2/mt_spm_dpidle.c"
| | | | wr = __spm_output_wake_reason(wakesta, pcmdesc, false);

---
# wake_reason_t __spm_output_wake_reason(const struct wake_status *wakesta,
				       const struct pcm_desc *pcmdesc, bool suspend)
| "이함수는 결국 wake up by WHO (reason)출력할라고  사용하는 함수"
| "wakesta->r12 에 wakeup 발생된 소스가 기술되어 있는듯."
| for (i = 1; i < 32; i++)
| | if (wakesta->r12 & (1U << i))
| | | if ((strlen(buf) + strlen(wakesrc_str[i])) < LOG_BUF_SIZE)
| | | | strncat(buf, wakesrc_str[i], strlen(wakesrc_str[i])); "buf에 저장됨"
| | | wr = WR_WAKE_SRC;
| spm_print(suspend, "wake up by%s, timer_out = %u, r13 = 0x%x, debug_flag = 0x%x\n",
| 		  buf, wakesta->timer_out, wakesta->r13, wakesta->debug_flag);

```

- (참고) spm_base 레지스터 주소 얻어오는 방법

```c

# void __spm_get_wakeup_status(struct wake_status *wakesta)
| wakesta->r12 = spm_read(SPM_SW_RSV_0);
"결국 SPM_SW_RSV_0 주소는 => 10006608임"
```

```c
"drivers/misc/mediatek/base/power/include/spm_v2/mt_spm_reg_mt6755.h"
#define SPM_SW_RSV_0                   (SPM_BASE + 0x608)

"drivers/misc/mediatek/base/power/include/spm_v2/mt_spm.h"
@ #define SPM_BASE spm_base
@ extern void __iomem *spm_base;
```

```c
# static void spm_register_init(void) # "drivers/misc/mediatek/base/power/spm_v2/mt_spm.c"
| node = of_find_compatible_node(NULL, NULL, "mediatek,sleep");
| spm_base = of_iomap(node, 0);
```

```dts
	sleep@10006000 {
		compatible = "mediatek,sleep";
		reg = <0x10006000 0x1000>;
	...}
```

- 참고
관련없는듯?

```c
# static int __init mt_eint_init(void)
| wakeup_source_init(&EINT_suspend_lock, "EINT wakelock");
```
> 아래처럼 나옴
> EINT wakelock	27		340		0		27		0		4985		1094		149190		0





#### wakeup_source 등록 및 사용 예
J1-ace과제, "drivers/samsung/extcon-sm5504.c"

```c
struct wakeup_source jig_suspend_wake;

wakeup_source_init(&jig_suspend_wake, "JIG_UART Connect suspend wake");

 "pm_stay_awake - Notify the PM core that a wakeup event is being processed."
__pm_stay_awake(&jig_suspend_wake);
pm_qos_update_request(&usbsw->qos_idle, PM_QOS_DEFAULT_VALUE);

 "__pm_relax - Notify the PM core that processing of a wakeup event has ended."
__pm_relax(&jig_suspend_wake);
pm_qos_update_request(&usbsw->qos_idle, PM_QOS_CPUIDLE_BLOCK_DEFAULT_VALUE);
```


#### `cat /sys/kernel/debug/wakeup_source` 하면 아래처럼 나옴

```sh
name		active_count	event_count	wakeup_count	expire_count	active_since	total_time	max_time	last_change	prevent_suspend_time
PowerManagerService.Broadcasts	1		1		0		0		0		142		142		52881		0
KeyEvents   	218		218		0		0		0		498		457		37017		0
PowerManagerService.Display	1		1		0		0		0		26780		26780		52738		0
NETLINK     	56		56		0		0		0		37		10		55752		0
[timerfd]   	0		0		0		0		0		0		0		12916		0
MT662x      	4		4		0		0		0		248		83		40463		0
binder      	2		2		0		0		0		7		7		31534		0
eventpoll   	58		59		0		0		0		0		0		55752		0
battery     	5		5		0		0		0		20		9		55750		0
ps          	1		1		0		0		0		8		8		8655		0
sec-battery-misc-event	0		0		0		0		0		0		0		8644		0
sec-battery-wc_headroom	0		0		0		0		0		0		0		8644		0
sec-battery-siop_event	0		0		0		0		0		0		0		8644		0
sec-battery-siop_level	0		0		0		0		0		0		0		8644		0
sec-battery-siop	0		0		0		0		0		0		0		8644		0
sec-battery-afc	0		0		0		0		0		0		0		8644		0
sec-battery-vbus	1		1		0		1		0		10026		10026		45000		0
sec-battery-cable	1		1		0		0		0		357		357		35330		0
sec-battery-monitor	4		4		0		0		0		448		155		55740		0
reactive_wake_lock	0		0		0		0		0		0		0		6750		0
s2mu005-charger	1		1		0		0		0		59		59		6715		0
fuel_alerted	0		0		0		0		0		0		0		6611		0
s2mu005-fuelgauge	1		1		0		0		0		129		129		6737		0
alarm       	4		5		0		0		0		36		31		53992		0
kpd wakelock	0		0		0		0		0		0		0		5763		0
nfc_wake_lock	2		6		0		2		0		4281		2286		40580		0
accdet key wakelock	0		0		0		0		0		0		0		3134		0
accdet irq wakelock	1		1		0		0		0		0		0		3144		0
accdet wakelock	0		0		0		0		0		0		0		3134		0
leds wakelock	0		0		0		0		0		0		0		3118		0
1-003d      	0		0		0		0		0		0		0		3098		0
alarmtimer  	0		0		0		0		0		0		0		2400		0
pmicAuxadc irq wakelock	46		46		0		0		0		200		22		54338		0
dlpt_notify_lock wakelock	3		3		0		0		0		123		106		52311		0
bat_percent_notify_lock wakelock	4		4		0		0		0		0		0		52188		0
pmicThread_lock_mt6328 wakelock	1		1		0		0		0		1		1		35137		0
EINT wakelock	22		248		0		22		0		3466		766		38630		0
autosleep   	0		0		0		0		0		0		0		540		0
```












### init_IRQ() 분석
mediatek MT6755 arm 기준

```c
# asmlinkage void __init start_kernel(void)
| ...
|---
| early_irq_init();
| init_IRQ();
| # void __init init_IRQ(void) "arch/arm/kernel/irq.c"
| | if (IS_ENABLED(CONFIG_OF) && !machine_desc->init_irq)
| | | irqchip_init();
| | # void __init irqchip_init(void) "drivers/irqchip/irqchip.c"
| | | of_irq_init(__irqchip_of_table);
| | | # void __init of_irq_init(const struct of_device_id *matches) "drivers/of/irq.c"
| | | | for_each_matching_node(np, matches) {
| | | | | if (!of_find_property(np, "interrupt-controller", NULL) ||
| | | |   "interrupt-controller 프로퍼티가 있는 모든 노드 탐색" //}
| | | | ...
| | | |	const struct of_device_id *match;
| | | | match = of_match_node(matches, desc->dev);
| | | | irq_init_cb = (of_irq_init_cb_t)match->data;
| | | |	ret = irq_init_cb(desc->dev, desc->interrupt_parent);
| | | | "struct of_device_id 의 .data()콜백이 호출됨"
| | | |---
| | | | ".data()콜백은 어디서 등록되나?"
| | | | "GIC등록 하는 코드 분석 drivers/irqchip/irq-mt-gic.c"
| | | | @ IRQCHIP_DECLARE(mt_gic, "mediatek,mt6735-gic", mt_gic_of_init);
| | | | | #define IRQCHIP_DECLARE(name, compat, fn) OF_DECLARE_2(irqchip, name, compat, fn) "drivers/irqchip/irqchip.h"
| | | | | #define OF_DECLARE_2(table, name, compat, fn) \
		_OF_DECLARE(table, name, compat, fn, of_init_fn_2) "include/linux/of.h"
| | | | | #define _OF_DECLARE(table, name, compat, fn, fn_type)			\
| | | | | 	static const struct of_device_id __of_table_##name		\
| | | | | 		__used __section(__##table##_of_table)			\
| | | | | 		 = { .compatible = compat,				\
| | | | | 		     .data = (fn == (fn_type)NULL) ? fn : fn  }
| | | | | "즉 .data() 콜백 에 mt_gic_of_init() 함수 등록됨"
| | | |---
|---
| ...
```
> 결국 DTS에서 interrupt-controller 로 기술된 모든 노드의 Driver에서 .data()로
> 등록된 콜백함수가 init_IRQ()에서 호출되는것임.
> 그 이후부터는 AP vendor specific한 Driver 등록 과정임 혹은 arm gic?




### irq_of_parse_and_map 함수

```c
"drivers/of/irq.c"
# unsigned int irq_of_parse_and_map(struct device_node *dev, int index)
```
> 위에서 한 코드 분석 내용 참고


### of_iomap() 분석
mediatek GIC등록 함수 mt_gic_of_init() 내에서 사용됨


```c
# int __init mt_gic_of_init(struct device_node *node, struct device_node *parent)
| dist_base = of_iomap(node, 0);
| cpu_base = of_iomap(node, 1);
| pol_base = of_iomap(node, 2);
| "두번째 매개변수, 0,1,2 의미?"
| "아래 dtsi파일 gic노드 내용을 보면 reg를 세개 가지고 있음, Mamory Mapped I/O 물리 메모리 주소임
| gic: interrupt-controller@10230000 {
| 	compatible = "mediatek,mt6735-gic";
| 	#interrupt-cells = <3>;
| 	#address-cells = <0>;
| 	interrupt-controller;
| 	reg = <0 0x10231000 0 0x1000>,
| 	      <0 0x10232000 0 0x1000>,
| 	      <0 0x10200620 0 0x1000>;
| };
| "
| # void __iomem *of_iomap(struct device_node *np, int index) "drivers/of/address.c"
| | "dts에서 파싱해온 물리주소를 Virtual 주소로 매핑하는 역할인듯?"
| | struct resource res;
| | of_address_to_resource(np, index, &res)
| | # int of_address_to_resource(struct device_node *dev, int index,
| | | addrp = of_get_address(dev, index, &size, &flags);
| | | "/* Get optional "reg-names" property to add a name to a resource */"
| | | of_property_read_string_index(dev, "reg-names",	index, &name);
| | | return __of_address_to_resource(dev, addrp, size, flags, name, r);
| | return ioremap(res.start, resource_size(&res));
| | @ #define ioremap(cookie,size)		__arm_ioremap((cookie), (size), MT_DEVICE)
| | # void __iomem * __arm_ioremap(phys_addr_t phys_addr, size_t size, unsigned int mtype)
| | | return arch_ioremap_caller(phys_addr, size, mtype, __builtin_return_address(0));
| | | # void __iomem *__arm_ioremap_caller(phys_addr_t phys_addr, size_t size, unsigned int mtype, void *caller)
| | | | return __arm_ioremap_pfn_caller(pfn, offset, size, mtype, caller);
| | | | # void __iomem * __arm_ioremap_pfn_caller(unsigned long pfn, "arch/arm/mm/ioremap.c"
| | | | | struct vm_struct *area;
| | | | | area = get_vm_area_caller(size, VM_IOREMAP, caller);
| | | | | # struct vm_struct *get_vm_area_caller(unsigned long size, unsigned long flags, "mm/vmalloc.c"
| | | | | | return __get_vm_area_node(size, 1, flags, VMALLOC_START, VMALLOC_END,
| | | | | | # static struct vm_struct *__get_vm_area_node(unsigned long size,
| | | | | | | va = alloc_vmap_area(size, align, start, end, node, gfp_mask);
| | | | | | | # static struct vmap_area *alloc_vmap_area(unsigned long size,
| | | | | | | | struct rb_node *n; "VM은 RB tree로 관리됨"
```
