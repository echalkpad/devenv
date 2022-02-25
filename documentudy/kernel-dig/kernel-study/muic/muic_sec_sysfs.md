

- usb_sel sysfs노드에서 지정한 값이 어떻게 boot_param에 기록되는지?

먼저 공정앱에서 command line을 만들어서 reset 명령을 때림.  

```java
"/android/vendor/samsung/packages/apps/MSP/FactoryTestPlus/FactoryKeystring/src/com/sec/android/app/shutdown/ShutdownPreference.java"
private void enable_uart(boolean command) {
	int uart_enable = command?1:0;
	int usb_sel = "PDA".equals(Support.Kernel.read(Support.Kernel.USB_SELECT))?1:0;
	int uart_sel = "AP".equals(Support.Kernel.read(Support.Kernel.UART_SELECT))?1:0;

	int switch_sel = uart_enable << 3 | uart_sel << 1 | usb_sel;
	LtUtil.log_d(CLASS_NAME, "onResume", "switch_sel : " + switch_sel);

	PowerManager pm = (PowerManager)getApplicationContext().getSystemService(Context.POWER_SERVICE);
	pm.reboot("swsel" + switch_sel);
}
```
> pm.reboot() 함수를 치면 결국 kernel에서 re boot 함수를 타게됨

```c
"kernel/reboot.c"
# SYSCALL_DEFINE4(reboot, int, magic1, int, magic2, unsigned int, cmd, void __user *, arg)
| switch (cmd)
| case LINUX_REBOOT_CMD_RESTART2:
| | ret = strncpy_from_user(&buffer[0], arg, sizeof(buffer) - 1);
| | "arg로 넘어온 값을 파싱 user에서 만든 swsel 이 포함된 cmd line임"
| | buffer[sizeof(buffer) - 1] = '\0';
| | kernel_restart(buffer);

| | # void kernel_restart(char *cmd)
| | | machine_restart(cmd);
| | | # void machine_restart(char *cmd) "arch/arm64/kernel/process.c"
| | | | if (arm_pm_restart)
| | | | | arm_pm_restart(reboot_mode, cmd);
```

```c
"drivers/staging/samsung/sec_reboot.c"
# static int __init sec_reboot_init(void)
| arm_pm_restart = sec_reboot;

# static void sec_reboot(enum reboot_mode reboot_mode, const char *cmd)
| if (cmd) 
| else if (!strncmp(cmd, "swsel", 5) && !kstrtoul(cmd + 5, 0, &value))
| | exynos_pmu_write(EXYNOS_PMU_INFORM3, SEC_RESET_SET_SWSEL | value);

```
> PMIC 의 register에 기록이가능



adb shell확인방법

```sh
 $ adb shell

 # reboot swsel3
"이후 부팅 로그에 pmic_info boot-param이 3으로 바뀐것을 확인할 수 있음"
```





### 만약 pmic_info의 두번째 비트가 0이면
uart_sel 드라이버에서 probe시에 AP uart path를 CP로 초기화함.
이경우는 keystring #*7284# 에서 
MODEM 선택 -> save and reboot 하면 바뀜






