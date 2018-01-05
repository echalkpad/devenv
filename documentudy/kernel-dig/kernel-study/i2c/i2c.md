## 목차    
  
## 1. I2C 동작 원리?      
## 2. I2C 구조 in kernel  
## 3. I2C 어떻게 초기화 되는지? (joon, exynoss7880에서)      
## 4. Driver 와 Device의 관계  
## 5. i2c 의 0번 채널에 muic가 어떻게 등록되는지?      
## 6. DT    
## 7. I2c write/read   
## 8. i2c adapter는 __도데체__ 무엇인가?    
## 9. 결론? 각 파일 역할은?    
## 10. 기타 API
## 11. gpio i2c 사용하기  
  
---  
  
http://www.programering.com/a/MjN1czNwATM.html    
    
# I2C in kerenl study      
  
Joon 과제 muic s2mu005 에서 사용되는 i2c 를 참고하여 작성.  
    
## 1. I2C 동작 원리?      
  
  
  
  
## 2. I2C 구조 in kernel  
  
Kernel의 I2c는 Buses 와 Devices로 나눌 수 있다.  
다시 Buses 는 Algorithms과 Adapters로 나뉜다.  
Devices는 Dirvers 와 Client로 나뉜다.   
    
I2C --- Buses ---- Algorithms --- struct i2c_algotithm  
    |          |  
    |           -- Adapters  ---- struct i2c_adapter  
    |  
    |  
     -- Devices --- Drivers --- struct i2c_driver  
                |    
                 -- Clients --- struct i2c_client  
  
    
  
  
## 3. I2C 어떻게 초기화 되는지? (joon, exynoss7880에서)      
  
  
  
  
## 4. Driver 와 Device의 관계  
  
Documentation/driver-model/porting.txt 참고하여 작성됨.    
  
- 전체 i2c bus 드라이버 등록함수        
    
```c    
# static int __init i2c_init(void)	"drivers/i2c/i2c-core.c"    
| | bus_register(&i2c_bus_type);    
```    
    
- 각 i2c 드라이버 bus에 등록      
    
```c    
i2c_add_driver(&dummy_driver);	"drivers/i2c/i2c-core.c"    
i2c_add_driver(&s2mu005_i2c_driver);	"drivers/mfd/s2mu005_core.c"    
```    
    
- device 등록 (device file 등록)      
이후에 다음 경로에 sysfs 파일이 생성됨.  /sys/bus/i2c/devices/*    
struct i2c_client 구조체가 device등록시에 필요한 구조체     
deviece 관련 구조체는 아래처럼 멤버 변수로 struct device 를 가지고 있음.    
```c    
struct pci_dev {  
	...  
	struct device dev;            /* Generic device interface */  
	...  
};  
struct i2c_client {    
	...    
	struct device dev;		/* the device structure		*/    
	...    
};    
```  
    
```c      
status = device_register(&client->dev);	"drivers/i2c/i2c-core.c"    
```    
    
    
- driver 등록       
이후에 다음 경로에 sysfs 파일이 생성됨.  /sys/bus/i2c/drivers/*    
struct i2c_driver 구조체가 driver등록시에 필요한 구조체     
driver관련 구조체는 멤버변수로 struct device_driver 를 가지고 있음.    
```c    
struct pci_driver {  
	...  
	struct device_driver driver;  
	...  
};    
struct i2c_driver {  
       ...  
	struct device_driver driver;  
       ...  
};  
```  
    
```c      
driver_register(&driver->driver);	"drivers/i2c/i2c-core.c"    
```    
이후에 Probe 호출됨     
    
  
- i2c 초기화 코드 seq    
    
```c      
exynos5_i2c_probe(struct platform_device *pdev)	"drivers/i2c/buses/i2c-exynos5.c"    
s3c24xx_i2c_probe(struct platform_device *pdev)	"drivers/i2c/buses/i2c-s3c2410.c"    
| s2mu005_i2c_probe(struct i2c_client *i2c,	"drivers/mfd/s2mu005_core.c"    
    
```      
  
  
    
## 5. i2c 의 0번 채널에 muic가 어떻게 등록되는지?      
  
등록 이후에 s2mu005->i2c를 이용해 i2c로 R/W함.      
struct i2c_client 자체는 represent an I2C slave device 임.    
s2mu005_i2c_probe에 전달된 i2c_client * 자체가 s2mu005를 위해 할당된 slave인듯.      
  
- 참고 구조체 선언    
    
```c    
static struct of_device_id s2mu005_i2c_dt_ids[] = {    
	{.compatible = "samsung,s2mu005mfd"},    
};    
static struct i2c_driver s2mu005_i2c_driver = {    
	.driver		= {    
		...    
		.of_match_table	= s2mu005_i2c_dt_ids,    
	},    
	.probe		= s2mu005_i2c_probe,    
	...    
};    
    
static int __init s2mu005_i2c_init(void)    
{    
	return i2c_add_driver(&s2mu005_i2c_driver);    
}    
subsys_initcall(s2mu005_i2c_init);    
```    
> i2c_add_driver() : 현재 i2c의 존재를 i2c 코어에 알린다.      
> i2c_add_driver()에서 s2mu005_i2c_driver구조체를 등록함      
    
    
- i2c_add_driver() 함수    
  
여기서 device와 driver 모두 register한다.      
| | | driver_register(&driver->driver);    
| | | | | | | | | | device_register(&client->dev);     <-- 호출 안됨  
    
```c      
static int __init s2mu005_i2c_init(void)	"drivers/mfd/s2mu005_core.c"    
| return i2c_add_driver(&s2mu005_i2c_driver);    
+ #define i2c_add_driver(driver) 		"include/linux/i2c.h"    
| | i2c_register_driver(THIS_MODULE, driver)    
| + int i2c_register_driver(struct module *owner, struct i2c_driver *driver)	"drivers/i2c/i2c-core.c"    
| | | driver_register(&driver->driver);    
| | + int driver_register(struct device_driver *drv)	"drivers/base/driver.c"      
| | | | bus_add_driver(drv);      
| | | + int bus_add_driver(struct device_driver *drv)	"drivers/base/bus.c"      
| | | | | driver_attach(drv);    
| | | | + int driver_attach(struct device_driver *drv)	"drivers/base/dd.c"    
| | | | | | bus_for_each_dev(drv->bus, NULL, drv, __driver_attach);	"drivers/base/bus.c"      
| | | | | + int bus_for_each_dev(struct bus_type *bus, struct device *start,    
		     void *data, int (*fn)(struct device *, void *))    
| | | | | | | error = fn(dev, data);      
| | | | | | + static int __driver_attach(struct device *dev, void *data)"drivers/base/dd.c"    
| | | | | | | | driver_probe_device(drv, dev);    
| | | | | | | + int driver_probe_device(struct device_driver *drv, struct device *dev)    
| | | | | | | | | ret = really_probe(dev, drv);    
| | | | | | | | + static int really_probe(struct device *dev, struct device_driver *drv)    
| | | | | | | | | | ret = dev->bus->probe(dev);    
| | | | | | | | | @ .probe		= i2c_device_probe, "drivers/i2c/i2c-core.c"    
| | | | | | | | | + static int i2c_device_probe(struct device *dev)    
| | | | | | | | | | | struct i2c_driver	*driver;    
| | | | | | | | | | | driver = to_i2c_driver(dev->driver);    
| | | | | | | | | | | status = driver->probe(client, i2c_match_id(driver->id_table, client));    
| | | | | | | | | | @ .probe		= s2mu005_i2c_probe, "drivers/mfd/s2mu005_core.c"    
| | | | | | | | | | | | s2mu005_i2c_probe(struct i2c_client *i2c,	"실제 driver i2c 설정 probe 호출"    
| | | i2c_for_each_dev(driver, __process_new_driver);    
| | + int i2c_for_each_dev(void *data, int (*fn)(struct device *, void *))    
| | | | bus_for_each_dev(&i2c_bus_type, NULL, data, fn);    
  
"s2mu005 i2c에서는 여기서부터 호출 안됨  
그럼device_register(&client->dev) 는 누가 호출함? -> 아래 8. 번 참고"  
| | | + int bus_for_each_dev(struct bus_type *bus, struct device *start,     
			void *data, int (*fn)(struct device *, void *))		"drivers/bus/bus.c"    
| | | | | error = fn(dev, data);  "s2mu005 i2c에서는 이 함수 호출 안됨"   
| | | | + static int __process_new_driver(struct device *dev, void *data)	"drivers/i2c/i2c-core.c"    
| | | | | | i2c_do_add_adapter(data, to_i2c_adapter(dev)); " data == s2mu005_i2c_driver "    
| | | | | | | #define to_i2c_adapter(d) container_of(d, struct i2c_adapter, dev)    
| | | | | + static int i2c_do_add_adapter(struct i2c_driver *driver, "driver == s2mu005_i2c_driver"    
			      struct i2c_adapter *adap)    
| | | | | | | i2c_detect(adap, driver);     
| | | | | | + static int i2c_detect(struct i2c_adapter *adapter, struct i2c_driver *driver)    
| | | | | | | | i2c_detect_address(temp_client, driver);    
| | | | | | | + static int i2c_detect_address(struct i2c_client *temp_client,    
| | | | | | | | | err = driver->detect(temp_client, &info); "<== 호출 안됨"  
| | | | | | | | | i2c_new_device(adapter, &info);    
| | | | | | | | + i2c_new_device(struct i2c_adapter *adap, struct i2c_board_info const *info)  
		"i2c_client 구초제의 각종 멤버 초기화 .dev 도 초기화"  
| | | | | | | | | | device_register(&client->dev); "drivers/base/core.c" "초기화 한 구조체 전달"    
| | | | | | | driver->attach_adapter(adap); ".attach_adapter는 안쓰는듯"      
    
```    
    
- bus_for_each_dev() 함수 seq       
bus == struct bus_type i2c_bus_type      
start == NULL      
data == s2mu005_i2c_driver      
fn == __process_new_driver()    
bus_type 관련 참고 : http://www.makelinux.net/ldd3/chp-14-sect-4    
    
```c      
int bus_for_each_dev(struct bus_type *bus, struct device *start,     
			void *data, int (*fn)(struct device *, void *))		"drivers/bus/bus.c"    
| struct device *dev;    
| klist_iter_init_node(&bus->p->klist_devices, &i,	"i->i_klist == bus->p->klist_devices"    
| + void klist_iter_init_node(struct klist *k, struct klist_iter *i,    
			  struct klist_node *n)		"lib/klist.c"    
| |     
| dev = next_device(&i)    
+ static struct device *next_device(struct klist_iter *i)	"drivers/bus/bus.c"    
| | dev_prv = to_device_private_bus(n);    
| + #define to_device_private_bus(obj)		container_of(obj, struct device_private, knode_bus)    
| | dev = dev_prv->device;    
| | return dev;    
| fn(dev, data); "dev가 뭘 가리키는 거임?"      
```    
  
- 참고 구조체 선언  
    
```c    
struct bus_type { 	"include/linux/device.h"    
	struct subsys_private *p;    
};    
struct bus_type i2c_bus_type = {    
	.name		= "i2c",    
	.match		= i2c_device_match,    
	.probe		= i2c_device_probe,    
	.remove		= i2c_device_remove,    
	.shutdown	= i2c_device_shutdown,    
	.pm		= &i2c_device_pm_ops,    
};    
```    
    
- i2c_new_device() 함수     
i2c_client 구조체멤버를 초기화하는 듯      
    
```c      
| i2c_new_device(adapter, &info);    
+ i2c_new_device(struct i2c_adapter *adap, struct i2c_board_info const *info)    
    
```    
    
    
- s2mu005_i2c_probe 함수  i2c_set_clientdata() 호출      
    
```c      
s2mu005_i2c_probe(struct i2c_client *i2c,	"drivers/mfd/s2mu005_core.c"    
| s2mu005->i2c = i2c;    
| i2c_set_clientdata(i2c, s2mu005);    
+ static inline void i2c_set_clientdata(struct i2c_client *dev, void *data)	"include/linux/i2c.h"    
| | dev_set_drvdata(&dev->dev, data);	    
| + static inline void dev_set_drvdata(struct device *dev, void *data)	"include/linux/device.h"    
| | | dev->driver_data = data;    
    
```      
> 결국 i2c->dev->driver_data = s2mu005;      
>```c    
> struct i2c_client {    
> 	...    
> 	struct device dev;		/* the device structure		*/    
> 	...    
> };    
    
    
## 6. DT    
    
회로도에 I2c 0번채널에 버스가 연결되어있음. i2c reg주소 offset은 13870000      
    
```dts      
"arch/arm64/boot/dts/exynos7880.dtsi"    
	/* I2C Channel 0 */    
	i2c_0: i2c@13870000 {    
		compatible = "samsung,s3c2440-i2c";    
		reg = <0x0 0x13870000 0x100>;    
		interrupts = <0 428 0>;    
		#address-cells = <1>;    
		#size-cells = <0>;    
		pinctrl-names = "default";    
		pinctrl-0 = <&i2c0_bus>;    
		clocks = <&clock 118>, <&clock 118>;    
		clock-names = "rate_i2c", "gate_i2c";    
		status = "disabled";    
	};    
    
"arch/arm64/boot/dts/exynos7880-joonlte_eur_open_00.dts"    
	i2c@13870000 {    
		status = "okay";    
		s2mu005@3d {    
			compatible = "samsung,s2mu005mfd";    
			reg = <0x3d>;    
			pinctrl-names = "default";    
			pinctrl-0 = <&if_irq &if_pmic_rstb>;    
			s2mu005,irq-gpio = <&gpa2 7 0>;    
    
			leds {    
				...    
			};    
    
			muic {    
				status = "okay";    
				muic,uart_addr = "139c0000.pinctrl";    
				muic,uart_rxd = "gpb1-0";    
				muic,uart_txd = "gpb1-1";    
			};    
		};    
	};    
```    
    
    
    
## 7. I2c write/read   
   
- I2C write function sequence (muic-s2mu005)      
    
s2mu005_i2c_guaranteed_wbyte(i2c, S2MU005_REG_MUIC_CTRL1, CTRL_MASK); "drivers/muic/s2mu005-muic.c"      
| s2mu005_i2c_write_byte(client, command, value); 	      
| | s2mu005_write_reg(client, command, value);		"drivers/mfd/s2mu005_core.c"      
| | | i2c_smbus_write_byte_data(i2c, reg, value);		"drivers/i2c/i2c-core.c"      
| | | | i2c_smbus_xfer      
| | | | | adapter->algo->smbus_xfer(adapter, addr, flags, read_write, command, protocol, data);      
| | | | | @ .smbus_xfer 콜백 없음      
| | | | | i2c_smbus_xfer_emulated(adapter, addr, flags, read_write, command, protocol, data);      
| | | | | | i2c_transfer(adapter, msg, num);      
| | | | | | | __i2c_transfer(adap, msgs, num);      
| | | | | | | | adap->algo->master_xfer(adap, msgs, num);      
| | | | | | | | @ .master_xfer		= s3c24xx_i2c_xfer, 	"/drivers/i2c/busses/i2c-s3c2410.c"        
    
    
```c      
s32 i2c_smbus_write_byte_data(const struct i2c_client *client, u8 command,      
		u8 value)      
{      
	union i2c_smbus_data data;      
	data.byte = value;      
	return i2c_smbus_xfer(client->adapter, client->addr, client->flags,      
			I2C_SMBUS_WRITE, command,      
			I2C_SMBUS_BYTE_DATA, &data);      
}      
EXPORT_SYMBOL(i2c_smbus_write_byte_data);      
```      
  
  
  
  
## 8. i2c_adapter는 __도데체__ 무엇인가?    
  
BUS를 나타내는 구조체이다.  
  
- source code    
  
파일이 두가지가 있는데 무슨 차이가 있는지 모르겠음. 둘다 i2c->adap을 등록함.    
"drivers/i2c/busses/i2c-exynos5.c" ==> high speed i2c  
"drivers/i2c/busses/i2c-s3c2410.c" ==> normal i2c 인듯?  
muic 는 아래것(normel i2c) 사용.    
위의 두 파일은 결국 i2c 버스를 나타내는 i2c_adapter를 등록하는 파일임.  
  
```c  
# static int exynos5_i2c_probe(struct platform_device *pdev) "drivers/i2c/busses/i2c-exynos5.c"  
| strlcpy(i2c->adap.name, "exynos5-i2c", sizeof(i2c->adap.name));  
| i2c->adap.algo    = &exynos5_i2c_algorithm;  
| i2c->adap.nr = -1;  
| ret = i2c_add_numbered_adapter(&i2c->adap);  
"위에것은 High Speed I2c용 임 : muic는 안씀"  
  
# static int s3c24xx_i2c_probe(struct platform_device *pdev) "drivers/i2c/busses/i2c-s3c2410.c"  
| struct s3c24xx_i2c *i2c;  
| else  
| 	s3c24xx_i2c_parse_dt(pdev->dev.of_node, i2c);  
| # s3c24xx_i2c_parse_dt(struct device_node *np, struct s3c24xx_i2c *i2c)  
| | struct s3c2410_platform_i2c *pdata = i2c->pdata;  
| | pdata->bus_num = -1; "/* i2c bus number is dynamically assigned */ "  
| | of_property_read_u32(np, "samsung,i2c-sda-delay", &pdata->sda_delay);  
| | of_property_read_u32(np, "samsung,i2c-slave-addr", &pdata->slave_addr);  
| | of_property_read_u32(np, "samsung,i2c-max-bus-freq",  
"위의 dts 값들은 s2mu005 노드에 기록되어있지 않음 "  
"참고 arch/arm64/boot/dts/exynos7880-joonlte_eur_open_00.dts"  
| i2c = devm_kzalloc(&pdev->dev, sizeof(struct s3c24xx_i2c), GFP_KERNEL);
| strlcpy(i2c->adap.name, "s3c2410-i2c", sizeof(i2c->adap.name));  
| i2c->adap.owner = THIS_MODULE;  
| i2c->adap.algo = &s3c24xx_i2c_algorithm;  
| i2c->adap.retries = 2;  
| i2c->adap.class = I2C_CLASS_DEPRECATED;  
| i2c->adap.algo_data = i2c;  
| i2c->adap.dev.parent = &pdev->dev;  
| i2c->adap.nr = i2c->pdata->bus_num;  
| i2c->adap.dev.of_node = pdev->dev.of_node;  
| ret = i2c_add_numbered_adapter(&i2c->adap);  
  
| # int i2c_add_numbered_adapter(struct i2c_adapter *adap) "drivers/i2c/i2c-core.c"  
| | if (adap->nr == -1) "/* -1 means dynamically assign bus id */"  
| | 	return i2c_add_adapter(adap);  
  
| | # int i2c_add_adapter(struct i2c_adapter *adapter)  
| | | if (dev->of_node) {  
| | | 	id = of_alias_get_id(dev->of_node, "i2c"); "여기서 id가 할당되는 i2c 넘버임"  
| | | 	if (id >= 0) {  
| | |		adapter->nr = id;  
| | |		return __i2c_add_numbered_adapter(adapter);	}  
| | |---  
| | | # static int __i2c_add_numbered_adapter(struct i2c_adapter *adap)  
| | | | id = idr_alloc(&i2c_adapter_idr, adap, adap->nr, adap->nr + 1, "아래 id 할당 참고"  
	       GFP_KERNEL);  
| | | | return i2c_register_adapter(adap);  
| | |---  
| | | id = idr_alloc(&i2c_adapter_idr, adapter,  
| | |		__i2c_first_dynamic_bus_num, 0, GFP_KERNEL);  
| | | adapter->nr = id; "bus number 등록"  
| | | return i2c_register_adapter(adapter);  
  
| | | # static int i2c_register_adapter(struct i2c_adapter *adap)  
| | | | dev_set_name(&adap->dev, "i2c-%d", adap->nr);  
| | | | adap->dev.bus = &i2c_bus_type; "adapter의 device 구조체 초기화"  
| | | | adap->dev.type = &i2c_adapter_type;  
| | | | res = device_register(&adap->dev); "device_register() !!"  
| | | | res = class_compat_create_link(i2c_adapter_compat_class, &adap->dev, "여기서 sysfs 등록할 듯 : 추후분석 요"  
				       adap->dev.parent);  
| | | | of_i2c_register_devices(adap);  
  
| | | | # static void of_i2c_register_devices(struct i2c_adapter *adap)   
"여기서 i2c_board_info구조체를 초기화함 dts 파일에서 값을 읽어서 구조체 초기화"  
"예전엔 board파일에서 초기화했었음"  
| | | | | for_each_available_child_of_node(adap->dev.of_node, node) {  
| | | | | struct i2c_board_info info = {};  
| | | | | if (of_modalias_node(node, info.type, sizeof(info.type)) < 0)  
| | | | | # int of_modalias_node(struct device_node *node, char *modalias, int len) "drivers/of/base.c"  
"dts파일에서 compatible의 samsung, 다음값을 info.type에 저장! "  
"참고 arch/arm64/boot/dts/exynos7880.dtsi"  
"	  
	i2c_0: i2c@13870000 {  
		compatible = "samsung,s3c2440-i2c";  
		...  
"  
| | | | | addr = of_get_property(node, "reg", &len);  
| | | | | info.addr = be32_to_cpup(addr);  
| | | | | info.irq = irq_of_parse_and_map(node, 0);  
| | | | | info.of_node = of_node_get(node);  
| | | | | info.archdata = &dev_ad;  
| | | | | if (of_get_property(node, "ten-bit-address", NULL))  
| | | | | 	info.flags |= I2C_CLIENT_TEN;  
| | | | | result = i2c_new_device(adap, &info);  
  
| | | | | # i2c_new_device(struct i2c_adapter *adap, struct i2c_board_info const *info)  
"i2c_client 구조체가 여기서 만들어짐 !"  
"i2c_board_info 구조체에서 저장된 값들로 i2c_client 구조체 변수를 초기화함"  
| | | | | | struct i2c_client	*client;  
| | | | | | client = kzalloc(sizeof *client, GFP_KERNEL);  
| | | | | | client->dev.platform_data = info->platform_data;  
| | | | | | client->flags = info->flags;  
| | | | | | client->addr = info->addr;  
| | | | | | client->irq = info->irq;  
| | | | | | strlcpy(client->name, info->type, sizeof(client->name)); "s3c2440-i2c"  
| | | | | | client->dev.parent = &client->adapter->dev;  
| | | | | | client->dev.bus = &i2c_bus_type;  
| | | | | | client->dev.type = &i2c_client_type;  
| | | | | | client->dev.of_node = info->of_node;  
| | | | | | status = device_register(&client->dev); "device_register() !! 위에서한거랑 어떤 차이인지 확인하기"  
  
  
```  
  
- 참고 구조체 선언    
  
```c  
static const struct i2c_algorithm exynos5_i2c_algorithm = {  
	.master_xfer		= exynos5_i2c_xfer,  
	.functionality		= exynos5_i2c_func,  
};  
```  
- sysfs 확인    
  
```sh  
shell@joonlte: $ ls /sys/class/i2c-adapter/  
  
i2c-0  
i2c-1  
i2c-2  
i2c-3  
i2c-4  
i2c-5  
i2c-6  
i2c-7  
i2c-8  
i2c-9  
```  
  
  
## 8.1. dev.of_node는 언제 누가 어떻게 등록?  
  
pdev->dev.of_node 에 exynos7880.dtsi 파일의 디바이스 노드가 연결되어 있는듯.  
(exynos7880-universal7880.dts) 일수도 있음...  
pdev->dev.of_node가 언제 초기화 되는지 찾기.  
  
```c  
static int s3c24xx_i2c_probe(struct platform_device *pdev)  
{  
	...	  
	if (!pdev->dev.of_node) { //}  
```  
  
--> platform_driver.md 참고  
  
  
  
  
  
  
  
## 8.2 I2c minor number는 어떻게 할당되고 어떤값으로 할당되는지 어떻게 아는가?  
  
/dev/i2c-* 번호는 minor number임 i2c의 Major number는 89  
각 adapter마다(SoC의 i2c bus마다) 하나의 minor number를 가짐.  
i2c_adapter->nr 변수에 번호가 저장되는듯  
  
  
log 를보면 s3c-i2c 의 probe함수가 각 adapter갯수만큼 호출된것을 알수 있음.  
device등록 이후에 driver가 등록될때, driver의 이름과 동일한 device의 이름이  
발견되면 probe호출됨. "s3c-i2c" 의 name을 갖는 platform_device(i2c_adapter?)가 많이 있다는 뜻.  
driver.name = "s3c-i2c" 가 platform_device와 같은 이름이면  probe가 호출 된다고함.  
(struct platform_device 의 멤버 name 과  struct platform_driver 의  멤버  
driver.name 은 동일한 값을 갖는다.  
http://forum.falinux.com/zbxe/index.php?document_srl=567697&mid=device_driver )  
  
----  
probe는 어떻게 여러번 호출되는가?  
platform_driver.md 파일 참고  
  
bus_type의 probe가 여러번 호출되는듯???  
> 아님 s3c-i2c adapter관련 probe 는 platform_driver(platform_bus)의 probe임  
  
----  
i2c 버스를 나타내는 i2c_adapter구조체를 초기화하는 probe함수가 호출되는  
순서대로 /dev/i2c-* 번호가 할당됨.   
exynos에서는 s3c24xx_i2c_probe(그냥i2c) , exynos5_i2c_probe(고속 i2c)이  
두함수가 그 초기화를 담당함. 만약 버스가 13개있으면 이 두 함수가 13번 호출됨  
  
근데 지금 아직 모르겠는건 저 두 probe함수가 어떤과정으로 여러번 호출 되는지임  
-->  아래 8.3 참고, platform_driver.md 파일 참고
  
  
  
  
- `(참고)` id할당  
http://egloos.zum.com/studyfoss/v/5187192    
http://lwn.net/Articles/103209/    
  
```c  
  
# int idr_alloc(struct idr *idr, void *ptr, int start, int end, gfp_t gfp_mask) "lib/idr.c"  
| struct idr_layer *pa[MAX_IDR_LEVEL + 1];  
| int id;  
| /* allocate id */  
| id = idr_get_empty_slot(idr, start, pa, gfp_mask, NULL);  
| idr_fill_slot(idr, ptr, id, pa);  
| return id;  
```  
  
  
## 8.3  exynos5 hs-i2c probe초기화 과정 분석!!   
  
# static int __init i2c_adap_exynos5_init(void) " initcall로 호출됨  subsys_initcall(i2c_adap_exynos5_init); "  
| return platform_driver_register(&exynos6_i2c_driver);  
.........  
driver_register  
  
| bus_for_each_dev(drv->bus, NULL, drv, __driver_attach);	"drivers/base/bus.c"        
| # int bus_for_each_dev(struct bus_type *bus, struct device *start,  
		     void *data, int (*fn)(struct device *, void *))  
| | "bus에 연결된 모든 dev탐색 - 각 bus의 probe가 어떻게 호출되는지 나타내는 핵심부분!! - probe.log 파일 참고"  
| | while ((dev = next_device(&i)) && !error)  
| | | error = fn(dev, data); "여기서 fn은 __driver_attach() 함수임"  
| | | # static int __driver_attach(struct device *dev, void *data)  
| | | | struct device_driver *drv = data;  
| | | | if (!driver_match_device(drv, dev))  
| | | | # static inline int driver_match_device(struct device_driver *drv, struct device *dev)  
| | | | | return drv->bus->match ? drv->bus->match(dev, drv) : 1; "bus_type의 .match가 여기서 실행됨"  
| | | | return 0;  
| | | | "platform bus로 연결된 모든 dev를 처음부터 탐색 dev와 drv가 일치하지 않으면 probe못하고 return"  
| | | | ...  
| | | | driver_probe_device(drv, dev); "비로소 match된 drv가 호출됨"  
  
  
반드시 읽기!!    
http://furmuwon.egloos.com/10928143  
  
init_call 관련  
http://blog.daum.net/baramjin/16010994  
  
  
## 8.4 i2c bus 초기화 과정  
  
  
  
  
  
  
  
## 9. 결론? 각 파일 역할은?    
  
"drivers/mfd/s2mu005_core.c"   
> i2c_driver -> driver_register() 	Driver 등록   
"drivers/i2c/busses/i2c-s3c2410.c"   
> i2c_adapter->dev -> device_register()  Bus 등록   
> i2c_client->dev  -> device_register()  slave를 BUS에 등록?  
> Adapter등록, Device 등록  
  
i2c_adapter는 i2c 버스마다 하나씩 가지고 있고, i2c_client는 각 i2c 디바이스마다 각각 가지고 있음?  
muic에 해당하는 client 를 가지고있음.?  
  
"drivers/muic/s2mu005_muic.c"  
> 여기서 i2c(i2c_client)는 reg R/W 할때만 사용, i2c 관련등록은 없음.  
  
  





  
  
## 10. 기타 API

참고 code drivers/mfd/max14577.c
```c
"drivers/mfd/max14577.c"
# static int max14577_i2c_probe(struct i2c_client *i2c,
| max14577->regmap = devm_regmap_init_i2c(i2c,
			&max14577_muic_regmap_config);
```

이렇게 등록한뒤

```c
"drivers/extcon/extcon-max14577.c"
# static int max14577_muic_detect_accessory(struct max14577_muic_info *info)
| ret = max14577_bulk_read(info->max14577->regmap,
| 		MAX14577_MUIC_REG_STATUS1, info->status, 2);
| # static inline int max14577_bulk_read(struct regmap *map, u8 reg, u8 *buf, int count)
| | return regmap_bulk_read(map, reg, buf, count);
```
이렇게 i2c write가능함
extcon에서 사용하는듯 추후 분석필요.  
이 max14577은 s2mu005,4 와 코드 구조가 유사하기때문에 참고해서 반영필요함.

http://furmuwon.egloos.com/m/11067957











## 11. gpio i2c 사용하기


compatible = "i2c-gpio";
에 따라서 sw i2c 를 쓰는지 hw i2c를 쓰는지 adapter가 결정됨.

cell-index는 뭐임? -> 그냥 주소개념 중복만 안되면됨

```dts
/* SENSOR SW I2C configurations */
&soc {
	i2c22: i2c@22 {
		cell-index = <22>;
		compatible = "i2c-gpio";
		gpios = <&pio 10 0	/* sda */
			&pio 11 0	/* scl */
			>;
		#i2c-gpio,delay-us = <2>;
		#address-cells = <1>;
		#size-cells = <0>;

		k2hh@1D {
			compatible = "k2hh-i2c";
			reg = <0x1D>;
			pinctrl-names = "default";
			pinctrl-0 = <&acc_int_active>;
			interrupt-parent = <&eintc>;
			interrupts = <66 IRQ_TYPE_EDGE_RISING>;
			k2hh,irq_gpio = <&pio 66 0>;
			k2hh,axis_map_x = <0>;
			k2hh,axis_map_y = <1>;
			k2hh,axis_map_z = <2>;
			k2hh,negate_x = <1>;
			k2hh,negate_y = <0>;
			k2hh,negate_z = <0>;
			k2hh,poll_interval = <100>;
			k2hh,min_interval = <2>;
		};
	};
};
```

아래 두개 파일로 다 등록됨

"drivers/i2c/busses/i2c-gpio.c" 참고
compatible = "i2c-gpio"; 을 가진 DTS node가 그리고 Driver가 전부 probe됨.

따라서 아래 platform_driver_register() 이후에 platform_bus의 연결되어있는 모든
platform device를 순회하면서  DTS에 compatible 로"i2c-gpio" 가진 노드가 있다면 모두 probe되는것임.
(platform device는 부팅후에 dts파일 파싱해서 바로 생성됨)

```c
"drivers/i2c/busses/i2c-gpio.c"
# static int __init i2c_gpio_init(void)
| ret = platform_driver_register(&i2c_gpio_driver);
```

```c
# static int i2c_gpio_probe(struct platform_device *pdev)
| struct i2c_algo_bit_data *bit_data;
| struct i2c_adapter *adap;
| if (pdev->dev.of_node)
| | ret = of_i2c_gpio_get_pins(pdev->dev.of_node, &sda_pin, &scl_pin);
| | # static int of_i2c_gpio_get_pins(struct device_node *np,
				unsigned int *sda_pin, unsigned int *scl_pin)
| | | 	*sda_pin = of_get_gpio(np, 0);
| | | 	*scl_pin = of_get_gpio(np, 1);
| | | "아래의 dts 내용을 순서대로 파싱해서 저장하는듯"
| | | "		gpios = <&pio 10 0	/* sda */
| | | 			&pio 11 0	/* scl */
| | | 			>;"
| ret = devm_gpio_request(&pdev->dev, sda_pin, "sda");
| ret = devm_gpio_request(&pdev->dev, scl_pin, "scl");
| "gpio request 등록!"
| priv = devm_kzalloc(&pdev->dev, sizeof( *priv), GFP_KERNEL); "adaptor 메모리할당"
| adap = &priv->adap;
| bit_data = &priv->bit_data;
| if (pdev->dev.of_node)
| | of_i2c_gpio_get_props(pdev->dev.of_node, pdata);
| | # static void of_i2c_gpio_get_props(struct device_node *np, "아래의 property 파싱함"
| | | of_property_read_u32(np, "i2c-gpio,delay-us", &pdata->udelay);
| | | if (!of_property_read_u32(np, "i2c-gpio,timeout-ms", &reg))
| | | of_property_read_bool(np, "i2c-gpio,sda-open-drain");
| | | of_property_read_bool(np, "i2c-gpio,scl-open-drain");
| | | of_property_read_bool(np, "i2c-gpio,scl-output-only");
| bit_data->setsda = i2c_gpio_setsda_dir; "bit_data 구조체 포인터 등록"
| bit_data->setscl = i2c_gpio_setscl_dir;
| bit_data->getsda = i2c_gpio_getsda;
| bit_data->udelay = 5;			/* 100 kHz */
| bit_data->timeout = HZ / 10;		/* 100 ms */
| ret = of_property_read_u32(pdev->dev.of_node, "cell-index", &pdev->id);
| adap->algo_data = bit_data;
| adap->nr = pdev->id;
| ret = i2c_bit_add_numbered_bus(adap);
```
	
```c
"drivers/i2c/algos/i2c-algo-bit.c"
int i2c_bit_add_numbered_bus(struct i2c_adapter *adap)
| return __i2c_bit_add_bus(adap, i2c_add_numbered_adapter);
| # static int __i2c_bit_add_bus(struct i2c_adapter *adap,
			     int (*add_adapter)(struct i2c_adapter *))
| | struct i2c_algo_bit_data *bit_adap = adap->algo_data;
| | "/* register new adapter to i2c module... */"
| | adap->algo = &i2c_bit_algo;
| | adap->retries = 3;
| | ret = add_adapter(adap);

@ const struct i2c_algorithm i2c_bit_algo = {
| .master_xfer		= bit_xfer,
| .functionality	= bit_func, }
" 결국 GPIO I2c 는 master_xfer 함수로 bit_xfer 함수가 등록됨"

```

- bit_xfer 함수 분석
실제 gpio를 bit banging하여 i2c 파형 만들어내는 함수  

```c
# static int bit_xfer(struct i2c_adapter *i2c_adap, struct i2c_msg msgs[], int num)
| i2c_start(adap);
| for (i = 0; i < num; i++) 
| | if (!(pmsg->flags & I2C_M_NOSTART)) 
| | | ret = bit_doAddress(i2c_adap, pmsg);
| | if (pmsg->flags & I2C_M_RD) 
| | | /* read bytes into buffer*/
| | | ret = readbytes(i2c_adap, pmsg);
| | else 
| | | /* write bytes from buffer */
| | | ret = sendbytes(i2c_adap, pmsg);
| i2c_stop(adap);

"i2c_start 함수만 일단분석 "
# static void i2c_start(struct i2c_algo_bit_data *adap)
| /* assert: scl, sda are high */
| setsda(adap, 0);
| udelay(adap->udelay);
| scllo(adap);

# define setsda(adap, val)	adap->setsda(adap->data, val)
| @ bit_data->setsda = i2c_gpio_setsda_dir; "drivers/i2c/busses/i2c-gpio.c"

| # static void i2c_gpio_setsda_dir(void *data, int state)
| | struct i2c_gpio_platform_data *pdata = data;
| | if (state)
| | | gpio_direction_input(pdata->sda_pin);
| | else
| | | gpio_direction_output(pdata->sda_pin, 0);
"결국 GPIO 컨트롤임"
```


참고 cell-index값이 뭔지?
cell-index 값은 결국 adap->nr 에 저장되는데 이값은 i2c bus 번호이다. (상위 코드분석 참고)
MT6737T 과제에서 HW i2c는 0~3 S/W i2c는 22,23,24로 dts에서 등록했음.
adaptor는 bus를 나타내는 구조체이기 때문에 버스별로 번호를 가지고있음!

```sh
 $ cat /sys/bus/i2c/devices
...
i2c-0
i2c-1
i2c-2
i2c-22
i2c-23
i2c-24
i2c-3
```

