
- Good document for tty in linux  
http://www.linusakesson.net/programming/tty/index.php
> 기가막힌 글임   

https://mug896.gitbooks.io/shell-script/content/tty.html
이것도 참조


커널내에서는 uart driver와 tty driver로 나눌수 있음.
uart driver : AP vendor의 물리적인 UART hw 블럭 컨트롤하는 드라이버
tty driver : 실제 user가 사용하는 /dev/tty* 디바이스 파일로 컨트롤되는 드라이버




console은 리눅스 부팅후 User와 OS가 서로 상호작용할(I/O) 수 있도록 해주는
터미널 디바이스. 커널에서는 tty driver 임
user가 os의 console을 이용하는 방법은 여러가지가 있는데 그중 대표적으로는

1. RS-232 같은 uart 시리얼로 I/O 하는 방법
> 보통 임베디드 시스템
2. 모니터+키보드 로 I/O하는 방법
> 데스크탑 시스템


다음 두 그림으로 이해하면 무척 쉬움.

1. UART통신을 이용한 콘솔 구조
![case1](./img/case1.png)

2. 모니터+키보드를 이용한 콘솔 구조
![case2](./img/case2.png)


결국 user는 tty driver를 사용해서 console을 다루게 된다.
tty device는 /dev/tty* 이 될것이다. 


중간에 Line discipline 은 BackSpace등 엔터 입력전까지 사용하는 버퍼 개념.  
(drivers/char/n_tty.c 가 이 드라이버 파일임)  

tty 드라이버는  
(drivers/char/tty_io.c )


(tty/serial/serial_core.c)는 tty 드라이버에서 serial쪽 담당인듯  


## 관련 device



/dev/pts/* 	: ssh 접속 콘솔 장치
/dev/tty*
/dev/console


- ssh 로 접속해서 아래같이 실험

1. LINUX PC
```sh 
 $ tty
 /dev/pts/28

 $
 hello
```

2. ssh 접속
```sh
 $ echo -e "\n hello" > /dev/pts/28
```


```sh
 # echo hello > /dev/console
 hello

```





## 관련 code 분석 (from MT6755 code )

- struct uart_driver  등록
 uart_register_driver()

```c
# static int __init mtk_uart_init(void) "drivers/misc/mediatek/uart/uart.c"
| mtk_uart_init_ports();
| # static int mtk_uart_init_ports(void)

| ret = uart_register_driver(&mtk_uart_drv);
| # int uart_register_driver(struct uart_driver *drv) "drivers/tty/serial/serial_core.c"
| | struct tty_driver *normal;
| | drv->tty_driver = normal;
| | normal->driver_name	= drv->driver_name;
| | normal->name		= drv->dev_name;
| | normal->major		= drv->major;
| | ... 
| | retval = tty_register_driver(normal);
| | # int tty_register_driver(struct tty_driver *driver) "drivers/tty/tty_io.c"
| | "uart_driver 구조체를 register할 때, 
| | uart_driver 구조체를 이용해 tty_driver구조체를 초기화함. 
| | 그 뒤 tty driver register!" 

```

- struct uart_port  등록
uart_add_one_port()

```c
# static int mtk_uart_probe(struct platform_device *pdev) "drivers/misc/mediatek/uart/uart.c"
| struct mtk_uart *uart;
| uart = &mtk_uarts[pdev->id];
| uart->port.dev = &pdev->dev;
| err = uart_add_one_port(&mtk_uart_drv, &uart->port);
| # int uart_add_one_port(struct uart_driver *drv, struct uart_port *uport) "drivers/tty/serial/serial_core.c"
```

- struct console 등록
register_console()

```c
# static int __init mtk_uart_console_init(void) "drivers/misc/mediatek/uart/uart.c"
| int err = mtk_uart_init_ports();
| register_console(&mtk_uart_console);
| # void register_console(struct console *newcon) "kernel/printk/printk.c"
```





## RIL (Radio Interface Layer)

미디어택에서는 uart_sel노드가 AP로만 유지되면됨.
uart H/W path를 CP로 변경할 필요없음 (S.LSI에서만 그런동작이 필요하다고 함)
아래 uart mode는 uart_sel 노드로 확인하는듯

UART mode : AP (normal mode)
        UART ↔ ATD ↔ RIL ↔ CP

UART mode : CP
	UART ↔ CP (S.LSI)
	UART ↔ Qcom diag ↔ CP (QC)

대부분 	QC : dev/ttyHSL0
	S.LSI : /dev/ttySAC2


## AT cmd관련 동작은 어떻게?

AT cmd는 MODEM에서 처리함.

