--------------------------------------------------------------------
# Platform Device Driver  

--------------------------------------------------------------------

#### 목차  
--------------------------------------------------------------------

> 1. Platform Bus  
> > 1.1. Device 와 Driver  
> > 1.2. Platform Bus는 무엇인가??  
> 2. Platform bus initialize    
> 3. platform_device 초기화    
> > 3.1. platform_device_register() 함수    
> > 3.2. Device Tree 기반에서는 platform_device 구조체를 어떻게 등록하나?      
> 4. platform_driver    
> > 4.1. platform_driver_register() 함수      
> 5. 추가 궁금한 사항   
> 6. References  

--------------------------------------------------------------------

## 1. platform bus  

### 1.1. Device 와 Driver  

간단히 말하면 Device는 H/W 이고 Driver는 S/W이다.  
Device는 struct device 로 표현되고 Driver는 struct device_driver로 표현된다.  
struct device 는 device_register()로 등록하고 device_driver는 driver_register()로 등록한다.  

platform bus world에서는 관련 구조체로 platform_device 와 platform_driver가 있다.   
platform_device는 struct device 의 포인터를 멤버로 갖고있고,  
platform_driver는 struct device_driver의 포인터를 멤버로 갖고있다.  

platform_device에는 커널에 등록을 원하는 각 Device의 H/W 종속적인 설정값들을 등록 하게 되어있다.  
platform_device의 초기화는 예전에는 board파일을 이용해서 했다. (arch/arm/mach-xx/mach-xxx.c)  
하지만 이제는 Device Tree를 이용한다. 커널 소스코드에 특정 설정값을 hard-coding하는 것을 방지하기 위해서다.  
(관련내용은 3.2 참고)  

platform_driver는 각 디바이스 드라이버 파일에서 초기화하고 등록한다. (drivers/*)   
platform_driver에는 device를 제어하기 위한 콜백함수 (probe(), resume(), shutdown() 등등)을  
구현하여 등록하게 되어있다. 그리고 platform_driver_register() API를 이용하여 커널에 등록한다.  
결국 driver_register()를 거쳐서 probe()가 호출된다.  
특이한점은, 이 함수가 진행될때, bus_type 인경우 Device와 Driver의 name이 같으면  
match되는 platform_driver 의 probe()를 모두 순차적으로 호출한 다는 점이다. (4.1참고)    

(참고 5)  
예전에는 platform_device 의 name과 platform_driver 의 name이 같은지 파악해서 driver의 probe를 호출 했으나,
Device Tree방식은 약간 다르다!!
결국 device_node에서 compatible 문자열과,
driver내에서 of_device_id의 compatible 문자열을 비교해서 matching 시키는것을 알 수 있음.
그거로 probe호출한다. platform_driver->driver.name 을 비교하는것이 아님!!!!


### 1.2. platform bus는 무엇인가??  
PC에는 많은 discoverable 한 디바이스 (PCI, USB등) 이 있지만,  
SoC 세계에는 아직도 non-discoverable 한 device들이 많다.  
커널은 그래서 실제 존재하는 hw가 무엇이있는지 알려줄 방법이 필요했다.  
platform device driver의 등장배경임.  

struct bus_type 구조체로 표현되는 bus는 platform bus, i2c, usb, spi등이 있다.  

http://lwn.net/Articles/448499/  

```txt  
  
In the very early days, Linux users often had to tell the kernel where specific  
devices were to be found before their systems would work. In the absence of  
this information, the driver could not know which I/O ports and interrupt  
line(s) the device was configured to use. Happily, we now live in the days of  
busses like PCI which have discoverability built into them; any device sitting  
on a PCI bus can tell the system what sort of device it is and where its  
resources are. So the kernel can, at boot time, enumerate the devices available  
and everything Just Works.  
  
Alas, life is not so simple; there are plenty of devices which are still not  
discoverable by the CPU. In the embedded and system-on-chip world,  
non-discoverable devices are, if anything, increasing in number. So the kernel  
still needs to provide ways to be told about the hardware that is actually  
present. "Platform devices" have long been used in this role in the kernel.  
This article will describe the interface for platform devices; it is meant as  
needed background material for a following article on integration with device  
trees.  
```

- platform bus 관련 구조체와 그의 초기화   

```c  
"drivers/base/platform.c"  
  
struct device platform_bus = {  
	.init_name	= "platform",  
};  
EXPORT_SYMBOL_GPL(platform_bus);  
  
struct bus_type platform_bus_type = {  
	.name		= "platform",  
	.dev_groups	= platform_dev_groups,  
	.match		= platform_match,  
	.uevent		= platform_uevent,  
	.pm		=  
		&platform_dev_pm_ops,  
};  
EXPORT_SYMBOL_GPL(platform_bus_type);  
  
int __init platform_bus_init(void)  
{  
	int error;  
  
	early_platform_cleanup();  
  
	error = device_register(&platform_bus);  
	if (error)  
		return error;  
	error =  
		bus_register(&platform_bus_type);  
	if  
		(error)  
			device_unregister(&platform_bus);  
	return  
		error;  
}  
```

--------------------------------------------------------------------

## 2. platform bus initialize  


```c  
# asmlinkage __visible void __init start_kernel(void) "init/main.c"  
| ...  
| setup_arch(&command_line);  
| ...  
| rest_init();  
| # static noinline void __init_refok rest_init(void)  
| | kernel_thread(kernel_init, NULL, CLONE_FS);  
| | # static int __ref kernel_init(void *unused)  
| | | kernel_init_freeable();  
| | | # static noinline void __init kernel_init_freeable(void)  
| | | | do_basic_setup();  
| | | | # static void __init do_basic_setup(void) "init/main.c"  
| | | | | driver_init();  
---  
# void __init driver_init(void) "drivers/base/init.c"  
| /* These are the core pieces */  
| devtmpfs_init();  
| devices_init();  
| buses_init();  
| classes_init();  
| firmware_init();  
| hypervisor_init();  
| /* These are also core pieces, but must come after the  
|  * core core pieces.  
|  */  
| platform_bus_init();  
| cpu_dev_init();  
| memory_dev_init();  
| container_dev_init();  
| }  
  
---  
| # int __init platform_bus_init(void)  
| | early_platform_cleanup();  
| | error = device_register(&platform_bus); "platform_bus이름의 device 구조체 register"  
| | # int device_register(struct device *dev)  
| | | device_initialize(dev);  
| | | return device_add(dev);  
| | | # int device_add(struct device *dev) "drivers/base/core.c"  
| | | | error = bus_add_device(dev);  
| | | | # int bus_add_device(struct device *dev) "drivers/base/bus.c"  
| | | | bus_probe_device(dev);  
| | | | # void bus_probe_device(struct device *dev) "drivers/base/bus.c"  
| | | | | ret = device_attach(dev);  
| | | | | " device_attach - try to attach device to a driver."  
| | | | | # int device_attach(struct device *dev) "drivers/base/dd.c"  
| | | | | | ret = device_bind_driver(dev);  
| | | | | | " device_bind_driver - bind a driver to one device."  
| | | | | | # int device_bind_driver(struct device *dev)  
| | | | | | | ret = driver_sysfs_add(dev);  
| | | | | | | if (!ret)  
| | | | | | | 	driver_bound(dev);  
| | | | | | | # static void driver_bound(struct device *dev)  
| | | | | | | | blocking_notifier_call_chain(&dev->bus->p->bus_notifier, BUS_NOTIFY_BOUND_DRIVER, dev);  
| | error = bus_register(&platform_bus_type); "추측-> 여기서 driver와  
device이름이 matching되면 probe호출 진행될듯??? --> 땡!! 아님."  
---  
" bus_register - register a driver-core subsystem"  
# int bus_register(struct bus_type *bus) "drivers/base/bus.c"  
| retval = add_probe_files(bus);  
| # static int add_probe_files(struct bus_type *bus)  
| | retval = bus_create_file(bus, &bus_attr_drivers_probe); "/sys/bus/platform/drivers_probe 생성 "  
| | retval = bus_create_file(bus, &bus_attr_drivers_autoprobe); "/sys/bus/platform/drivers_autoprobe 생성 "  
| | # int bus_create_file(struct bus_type *bus, struct bus_attribute *attr)  
| | | error = sysfs_create_file(&bus->p->subsys.kobj, &attr->attr);  
| retval = bus_add_groups(bus, bus->bus_groups);  
---  
  
```
> 일반 platform bus는 init할때 probe를 따로 호출하지 않는듯?  
> i2c bus는 probe호출 할듯 : 찾아보기  

  

- `(참고: 중요)` 아래와같이 platform bus이외의 다른 bus들도 bus_register()로 등록됨.    

  ​
```c  
return bus_register(&amba_bustype);  
err = bus_register(subsys);  
error = bus_register(&platform_bus_type);  
ret = bus_register(&hid_bus_type);  
retval = bus_register(&i2c_bus_type); "i2c bus" "i2c 도 adapter 에따른 probe호출이 여기서 일어남?"  
ret = bus_register(&iio_bus_type);  
error = bus_register(&serio_bus);  
ret = bus_register(&media_bus_type);  
return bus_register(&mmc_bus_type);  
return bus_register(&sdio_bus_type);  
error = bus_register(&scsi_bus_type);  
status = bus_register(&spi_bus_type);  
retval = bus_register(&usb_bus_type);  
ret = bus_register(&pmu_bus);  
```

--------------------------------------------------------------------

## 3. platform_device 초기화  

### 3.1. platform_device_register() 함수  

예전 board방식에서만 사용되고 현재 DT기반에서는 사용안함.  

```c  
# int platform_add_devices(struct platform_device **devs, int num) "drivers/base/platform.c"  
| for (i = 0; i < num; i++) {  
| 	ret = platform_device_register(devs[i]);  
| 	...  
| }  
---  
# int platform_device_register(struct platform_device *pdev) "drivers/base/platform.c"  
| device_initialize(&pdev->dev);  
| arch_setup_pdev_archdata(pdev);  
| return platform_device_add(pdev);  
```

  

`(참고)` Mini-2440 보드, 예전 board파일 방식에서  platform_add_devices사용.  
학생때 썻던 mini-2440 보드 기준    
한 보드 파일에서 모든 Platform_device 구조체를   
platform_add_deivce()로 넘겨서 등록함.  

```c  
# static void __init mini2440_init(void) "arch/arm/mach-s3c24xx/mach-mini2440.c"  
| ... "보드관련 내용 initialize"  
| platform_add_devices(mini2440_devices, ARRAY_SIZE(mini2440_devices));  
| # int platform_add_devices(struct platform_device **devs, int num) "drivers/base/platform.c"  
| | for (i = 0; i < num; i++) {  
| | 	ret = platform_device_register(devs[i]);	//}  
---  
@ static struct platform_device *mini2440_devices[] __initdata = {  
|       &s3c_device_ohci,  
|       &s3c_device_wdt,  
|       ...  
|       "보드에 필요한 device의 platform_device구조체 포인터들"  
|	...  
|   }  
@ struct platform_device s3c_device_ohci = {  
|       .name		= "s3c2410-ohci",  
|       ...  
|   }  
```

`(참고) Raspberry PI 2 의 board파일   
dts파일도 있지만 일부 platform_device는 예전 보드방식을 사용해서 등록함.    

```c  
# void __init bcm2709_init(void) "arch/arm/mach-bcm2709/bcm2709.c"  
| ...  
| bcm_register_device_dt(&w1_device);  
| bcm_register_device_dt(&bcm2708_fb_device);  
| @ #define bcm_register_device_dt(pdev)  if (!use_dt) bcm_register_device(pdev)  
| # int __init bcm_register_device(struct platform_device *pdev)  
| | ret = platform_device_register(pdev);  
| ...  
---  
@ static struct platform_device bcm2708_fb_device = {  
| 	.name = "bcm2708_fb",  
| 	.id = -1,		/* only one bcm2708_fb */  
| 	.resource = NULL,  
| 	.num_resources = 0,  
| 	.dev = {  
| 		.dma_mask = &fb_dmamask,  
| 		.coherent_dma_mask = DMA_BIT_MASK(DMA_MASK_BITS_COMMON),  
| 		},  
| };  
  
```

`(찾아보기)` device tree 기반에서는 platform_device 구조체를 어떻게 등록하나?    

  

--------------------------------------------------------------------

  

### 3.2. Device Tree 기반에서는 platform_device 구조체를 어떻게 등록하나?    

of_platform_bus_create()가 핵심 함수.    
재귀함수이며, 모든 노드를 탐색하여 platform_device를 초기화 함.  
첫번째 인자 *bus가 device_node포인터인데 각 디바이스의 platform_device에  
등록되는 포인터이다.  
pdev.dev->of_node 에 *bus가 연결됨!!!  


세가지 관련 함수가 있음.    
>  
- setup_machine_fdt(__fdt_pointer);  
  초기 board관련 dt 초기화.    
  (참고파일) device_tree.md     
- unflatten_device_tree();  
  dtb에 있는 내용을 파싱하여 device_node 구조체 생성및 초기화.    
  (참고파일) device_tree.md      
- of_platform_populate();  
  platform_device 초기화  
  각 platform_device의 device_node연결    
  (참고파일) platform_driver.md      


```c  
# static int __init arm64_device_init(void) "arch/arm64/kernel/setup.c"  
| {  
| 	of_platform_populate(NULL, of_default_bus_match_table, NULL, NULL);  
| 	return 0;  
| }  
| arch_initcall_sync(arm64_device_init);  
"arm64_device_init() 가 setup_arch() 이후에 호출되는지 확인필요"  
---  
# int of_platform_populate(struct device_node *root, "drivers/of/platform.c"  
			... , struct device *parent)  
| struct device_node *child;  
| root = root ? of_node_get(root) : of_find_node_by_path("/");  
|---  
| "of_allnodes(전체 DT노드의 root노드인듯?) 에서 root노드를 가져옴"  
| # struct device_node *of_find_node_by_path(const char *path) "drivers/of/base.c"  
|---  
| for_each_child_of_node(root, child)  
| 	rc = of_platform_bus_create(child, matches, lookup, parent, true);  
|---  
| " @bus: *bus는 각 개별 device_node 의 포인터임"   
| " @lookup: auxdata table for matching id and platform_data with device nodes"  
| # static int of_platform_bus_create(struct device_node *bus,  
				  ... , const struct of_dev_auxdata *lookup  
				  , struct device *parent, bool strict)  
| | struct platform_device *dev;  
| | const char *bus_id = NULL;  
| | auxdata = of_dev_lookup(lookup, bus);  
| | bus_id = auxdata->name;  
| | dev = of_platform_device_create_pdata(bus, bus_id, platform_data, parent);  
| | "platform_device 와 device_node연결이 이 함수에서 부터 시작됨"   
| | " *bus는 어디서 alloc되었나??? -> device_tree.md참고"  
| |---   
| | " of_platform_device_create_pdata - Alloc, initialize and register an of_device "  
| | # static struct platform_device *of_platform_device_create_pdata(  
					struct device_node *np,  
| | | struct platform_device *dev;  
| | | if (!of_device_is_available(np) || "dts에 status okay가 아니면 return"  
| | | dev = of_device_alloc(np, bus_id, parent);  
| | |---   
| | | " of_device_alloc - Allocate and initialize an of_device"  
| | | # struct platform_device *of_device_alloc(struct device_node *np,  
| | | | struct platform_device *dev;  
| | | | struct resource *res, temp_res;  
| | | | dev = platform_device_alloc("", -1);  
| | | |---   
| | | | # struct platform_device *platform_device_alloc(const char *name, int id) "drivers/base/platform.c"  
| | | | | struct platform_object *pa;  
| | | | | pa = kzalloc(sizeof( *pa) + strlen(name) + 1, GFP_KERNEL); "pdev 메모리할당"  
| | | | | pa->pdev.name = pa->name;  
| | | | | device_initialize(&pa->pdev.dev); "device_initialize!! - device구조체 초기화"  
| | | | | # void device_initialize(struct device *dev) "drivers/base/core.c"  
| | | | | return pa ? &pa->pdev : NULL;  
| | | |---   
| | | | res = kzalloc(sizeof( *res) * (num_irq + num_reg), GFP_KERNEL);  
| | | | dev->resource = res;  
| | | | dev->dev.of_node = of_node_get(np); "of_node_get 문제있음 아래 참고"  
| | | | "여기서 드디어 각 드라이버의 pdev->dev.of_node 가 등록됨!"  
| | | | dev->dev.parent = parent;  
| | | | dev_set_name(&dev->dev, "%s", bus_id); "kobj 구조체 .name에 이름 초기화"  
| | | | of_device_make_bus_id(&dev->dev); "이름 초기화 좀더 공부하기"  
| | |---   
| | | dev->dev.bus = &platform_bus_type;  
| | | dev->dev.platform_data = platform_data;  
| | | if (of_device_add(dev) != 0) { //}  
| | | return dev;  
| | |---   
| | | # int of_device_add(struct platform_device *ofdev) "drivers/of/device.c"  
| | | | set_dev_node(&ofdev->dev, of_node_to_nid(ofdev->dev.of_node));  
| | | | return device_add(&ofdev->dev); "sysfs노드를 만들고, udevd에 uevent를 날리는 아주 중요한 함수임"  
| | |---   
| |---   
| | for_each_child_of_node(bus, child)  
| | 	rc = of_platform_bus_create(child, matches, lookup, &dev->dev, strict); "재귀호출"  
|---  
| of_node_put(root);  
  
```

- `(참고)` for_each_child_of_node 가 어떤 동작을 하는지 분석하기.  

```c  
#define for_each_child_of_node(parent, child) \ "include/linux/of.h"  
	for (child = of_get_next_child(parent, NULL); child != NULL; \  
	     child = of_get_next_child(parent, child))  
---  
# struct device_node *of_get_next_child(const struct device_node *node,  
| next = __of_get_next_child(node, prev);  
---  
  
#define __for_each_child_of_node(parent, child) \  
	for (child = __of_get_next_child(parent, NULL); child != NULL; \  
	     child = __of_get_next_child(parent, child))  
---  
# static struct device_node *__of_get_next_child(const struct device_node *node,  
						struct device_node *prev)  
	struct device_node *next;  
	next = prev ? prev->sibling : node->child;  
  
	for (; next; next = next->sibling)  
		if (of_node_get(next))  
			break;  
	of_node_put(prev);  
	return next;  
```

- `(참고)`   of_node_get() 함수가 CONFIG_OF_DYNAMIC 이 enable안되어있어서 dummy함수로 연결됨.    

  ​
--------------------------------------------------------------------


## 4. platform_driver  

### 4.1. platform_driver_register() 함수    

platform_driver_register()는 각 디바이스 드라이버를 등록할 때 사용하는 API이다.  
보통 initcall로 호출된다.   
그리고 이 함수가 호출되면 platform bus 의 모든 device와 driver가 match되는지  
판단해서 match되면 really_probe를 통해서 드라이버의 probe를 호출한다.  
(정확하게는 platform_driver->device_driver.name과 platform_device.name이 같은지 비교함)  
match만 되면 모든 driver의 probe를 호출하기 때문에, (같은 bus라면) 동시에 순차적으로 여러 probe가 호출 될 수 있다.  
match 콜백은 각 bus_type 구조체의 .match 사용  

(예)  
struct platform_driver s3c24xx_i2c_driver : i2c adapter 여러개가 한꺼번에 순차적으로 probe됨  
s3c24xx_i2c_driver 의 device_driver.name은 s3c-i2c 임.  
모든 platform_device를 뒤져서 .name이 s3c-i2c 이면 그 platform_device 포인터를 이용해  
결국 platform_driver의 probe호출함. probe가 호출되는 순서대로 /dev/i2c-* 의 번호가 할당됨.  

  


- platform_driver_register() 가 driver_register()를 호출하는 과정  

```c        
return platform_driver_register(&mmp_dsi_driver);    
@ #define platform_driver_register(drv)	 __platform_driver_register(drv, THIS_MODULE)	"include/linux/platform_device.h"    
# int __platform_driver_register(struct platform_driver *drv,    
      			struct module *owner)	"drivers/base/platform.c"    
| drv->driver.bus = &platform_bus_type;  
| drv->driver.probe = platform_drv_probe;    
---    
| # static int platform_drv_probe(struct device *_dev)    
| | struct platform_driver *drv = to_platform_driver(_dev->driver);    
| | struct platform_device *dev = to_platform_device(_dev);    
| | ret = drv->probe(dev);    
---    
| drv->driver.remove = platform_drv_remove;    
| drv->driver.shutdown = platform_drv_shutdown;    
| return driver_register(&drv->driver); "driver_register()"   
```

- i2c_add_driver() 가 driver_register()를 호출하는 과정  

```c  
return i2c_add_driver(&s2mu005_i2c_driver); "drivers/mfd/s2mu005_core.c"  
@ #define i2c_add_driver(driver) i2c_register_driver(THIS_MODULE, driver)  
| # int i2c_register_driver(struct module *owner, struct i2c_driver *driver) "drivers/i2c/i2c-core.c"  
| | driver->driver.owner = owner;  
| | driver->driver.bus = &i2c_bus_type;  
| | res = driver_register(&driver->driver); "driver_register()"   
```

- driver_register() 함수 정의  

```c        
# int driver_register(struct device_driver *drv)    
| ret = bus_add_driver(drv);    
| # int bus_add_driver(struct device_driver *drv)    
| | driver_attach(drv);      
| | # int driver_attach(struct device_driver *drv)	"drivers/base/dd.c"      
| | | bus_for_each_dev(drv->bus, NULL, drv, __driver_attach);	"drivers/base/bus.c"        
| | | # int bus_for_each_dev(struct bus_type *bus, struct device *start, " *여기서 bus에 연결된 probe모두 호출됨"  
    	     void *data, int (*fn)(struct device *, void *))      
| | | | "bus에 연결된 모든 dev탐색 - 각 bus의 probe가 어떻게 호출되는지 나타내는 핵심부분!! - probe.log 파일 참고"  
| | | | while ((dev = next_device(&i)) && !error)  
| | | | 	error = fn(dev, data); "여기서 fn은 __driver_attach() 함수임"  
| | | | # static int __driver_attach(struct device *dev, void *data)"drivers/base/dd.c"      
| | | | | struct device_driver *drv = data;  
| | | | | if (!driver_match_device(drv, dev))  
| | | | | 	return 0;  
| | | | | "platform bus로 연결된 모든 dev를 처음부터 탐색 dev와 drv가 일치하지 않으면 probe못하고 return"  
| | | | | "연결된 모든 dev가 탐색되는데 대부분 걸러짐"
| | | | | # static inline int driver_match_device(struct device_driver *drv, struct device *dev)  
| | | | | | return drv->bus->match ? drv->bus->match(dev, drv) : 1; "bus_type의 .match가 여기서 실행됨"  
| | | | | | "platform bus의 경우 platform_match() 가 실행됨, 아래 코드 참고"
| | | | | | @ struct bus_type platform_bus_type = {   "drivers/base/platform.c"
| | | | | | | 	.name		= "platform",
| | | | | | | 	.match		= platform_match,
| | | | | | | 	...}  
| | | | | ...  
| | | | | driver_probe_device(drv, dev); "비로소 match된 drv가 호출됨"  
| | | | | # int driver_probe_device(struct device_driver *drv, struct device *dev)      
| | | | | | ret = really_probe(dev, drv);      
| | | | | | # static int really_probe(struct device *dev, struct device_driver *drv)      
| | | | | | | if (dev->bus->probe) "platform_driver_register 가 bus_type이면 여기가 호출됨"  
| | | | | | | 	ret = dev->bus->probe(dev);  
| | | | | | | else if (drv->probe)  
| | | | | | | 	ret = drv->probe(dev);    
| | | | | | | @ drv->driver.probe = platform_drv_probe;    
| | | | | | | # static int platform_drv_probe(struct device *_dev)	"drivers/base/platform.c"    
| | | | | | | | struct platform_driver *drv = to_platform_driver(_dev->driver);    
| | | | | | | | struct platform_device *dev = to_platform_device(_dev);    
| | | | | | | | ret = drv->probe(dev); "결국 platform_driver->prove() 호출"    
| | | | | | | | @ .probe	= mmp_dsi_probe, "drivers/video/mmp/hw/mmp_dsi.c"    
| | | | | | | driver_bound(dev);  
```

  

  

--------------------------------------------------------------------


## 5. 추가 궁금한 사항   
--------------------------------------------------------------------


#### Source code tracking of platform driver registering function  
	from "drivers/i2c/buses/i2c-s3c2410.c"  
	in point of views that how to connect between DT and driver.  


```c  
  
# static int __init i2c_adap_s3c_init(void)  
| return platform_driver_register(&s3c24xx_i2c_driver);  
| @ #define platform_driver_register(drv)  __platform_driver_register(drv, THIS_MODULE)   
 "include/linux/platform_device.h"  
| # int __platform_driver_register(struct platform_driver *drv,  "drivers/base/platform.c"  
| | return driver_register(&drv->driver);  
| | # int driver_register(struct device_driver *drv) "drivers/base/driver.c"  
| | | other = driver_find(drv->name, drv->bus);  
| | | ret = bus_add_driver(drv);  
| | | ret = driver_add_groups(drv, drv->groups);  
| | | kobject_uevent(&drv->p->kobj, KOBJ_ADD);  
  
```

  

--------------------------------------------------------------------

#### of_match_table 은 어떻게 사용되는지    
of_match_device()로   
device tree : of_match_table 어떻게 pdev->dev.of_node 와 연결?되는지  

예전에는 platform_device 의 name과 platform_driver 의 name이
같은지 파악해서 driver의 probe를 호출 했으나,
Device Tree방식은 약간 다르다!!
결국 device_node에서 compatible 문자열과,
driver내에서 of_device_id의 compatible 문자열을 비교해서 matching 시키는것을 알 수 있음.
그거로 probe호출한다. platform_driver->driver.name 을 비교하는것이 아님!!!!

```c  
@ struct bus_type platform_bus_type = {   "drivers/base/platform.c"
| 	.name		= "platform",
| 	.match		= platform_match,
| 	...}  
# static int platform_match(struct device *dev, struct device_driver *drv)
| "Device Tree 형식의 match 방식"
| /* Attempt an OF style match first */
| if (of_driver_match_device(dev, drv))  
| 	return 1;
| # static inline int of_driver_match_device(struct device *dev, "include/linux/of_device.h"  
| | return of_match_device(drv->of_match_table, dev) != NULL;  
| @ .of_match_table	= s2mu005_i2c_dt_ids, "drivers/mfd/s2mu005_core.c"  
| | | static struct of_device_id s2mu005_i2c_dt_ids[] = {  
| | | 	{.compatible = "samsung,s2mu005mfd"}, }  
| |--- 
| | # const struct of_device_id *of_match_device(const struct of_device_id *matches,"drivers/of/device.c"
| | | return of_match_node(matches, dev->of_node);
| | | # const struct of_device_id *of_match_node(const struct of_device_id *matches,
					 const struct device_node *node) "drivers/of/base.c"
| | | | 	match = __of_match_node(matches, node);
| | | | # const struct of_device_id *__of_match_node(const struct of_device_id *matches,
| | | | | for (; matches->name[0] || matches->type[0] || matches->compatible[0]; matches++) {
| | | | | 	score = __of_device_is_compatible(node, matches->compatible,
| | | | | 						  matches->type, matches->name);
| | | | | ... }
| | | | | # static int __of_device_is_compatible(const struct device_node *device,
| | | | | | prop = __of_find_property(device, "compatible", NULL);
| | | | | | "결국 device_node에서 compatible 문자열과,
| | | | | | driver내에서 of_device_id의 compatible 문자열을 비교해서 probe호출한다"
| | | | | | "platform_driver->driver.name 을 비교하는것이 아님!!!!"
| |--- 
  
```

- `비교참고` i2c bus에서 of_match_table 사용  

```c
@ struct bus_type i2c_bus_type = { "drivers/i2c/i2c-core.c"
| 	.name		= "i2c",
| 	.match		= i2c_device_match,
| 	...}
# static int i2c_device_match(struct device *dev, struct device_driver *drv)
| /* Attempt an OF style match */
| if (of_driver_match_device(dev, drv))
| 	return 1;
| # static inline int of_driver_match_device(struct device *dev, "include/linux/of_device.h"  
| | return of_match_device(drv->of_match_table, dev) != NULL;  
```



--------------------------------------------------------------------

#### 모든 device는 device_initialize(dev) 를 한다.  

확인해보기  

--------------------------------------------------------------------

### 6. References

Linux Kernel 3.18.14  
http://lwn.net/Articles/448499/   
Platform D/D name으로 matching
http://furmuwon.egloos.com/10928143  
init_call 관련  
http://blog.daum.net/baramjin/16010994  
Documentation/driver-model/porting.txt
