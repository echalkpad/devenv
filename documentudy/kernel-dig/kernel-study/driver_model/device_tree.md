

#### 기초 사항  

----
.dtsi : SoC 에대한 속성이 기록됨.
.dts :  board 에대한 속성 

----
device tree 의 내용과 platform driver를 연결해 주는 것은 compatible 속성이다.  
compatible을 찾아서 실제 드라이버에서 pdev.dev->of_node로 연결시켜 주는듯.  


----
- /soc 의 자식 노드는 memory mapped device 임!!  
> The children of the /soc node are memory mapped devices.  
----
dev.platform_data 는 디바이스트리를 사용할지말지 결정하는 포인터? 아래를 읽어볼것
```txt
from LWN..

Drivers expecting platform data should check the dev.platform_data pointer in
the usual way. If there is a non-null value there, the driver has been
instantiated in the traditional way and device tree does not enter into the
picture; the platform data should be used in the usual way. If, however, the
driver has been instantiated from the device tree code, the platform_data
pointer will be null, indicating that the information must be acquired from the
device tree directly.

In this case, the driver will find a device_node pointer in the platform
devices dev.of_node field. The various device tree access functions
(of_get_property(), primarily) can then be used to extract the needed
information from the device tree. After that, it`s business as usual.
```

----
모듈로 DT를 사용할때, of_device_id 구조체 인스턴스 포인터는 아래와 같이 초기화.  
    MODULE_DEVICE_TABLE(of, my_of_ids);


----
dts의 값들이 of_node 구조체 포인터에 어떻게 저장되는가?


----

#### driver에서 사용할 수 있는 property value 얻는 API


````c	
/* clocks property */

	s->clk = clk_get(&pdev->dev, NULL);

/* reg property */

	r = platform_get_resource(pdev, IORESOURCE_MEM, 0);

/* interrupts property */

	s->irq = platform_get_irq(pdev, 0);

/* dmas property */

	s->rx_dma_chan = dma_request_slave_channel(s->dev, "rx");
	s->tx_dma_chan = dma_request_slave_channel(s->dev, "tx");

/* 사용자 정의 property */

	struct device_node *np = pdev->dev.of_node;
	if (of_get_property(np, "fsl,uart-has-rtscts", NULL))
````

----


#### 디바이스 트리 초기화는 어떻게?

drivers/of/fdt.c 랑 pdt.c 두가지가 있음.
(Flattened Device Tree) : uboot이 이걸사용함?

"drivers/of/pdt.c" 근데 joon과제에서 Makefile을 보니까 pdt.c는 빌드안됨.
obj-$(CONFIG_OF_FLATTREE) += fdt.o
obj-$(CONFIG_OF_PROMTREE) += pdt.o

일단 dtc가 보드환경에 맞는 dts dtsi파일을 컴파일해서 dtb를 만듦.  
어떤 dts,i를 빌드할지는 유져가 결정함. 커널이 알아서 찾는거 아님.

joon과제 기준 dts빌드과정은 아래 빌드스크립트에서
buildscript/build_common/build_api/build_api.build

```sh
아래 키워드 참고
... 
function build_kernelconf_ext_slsi 
...
if [ "$dt" == "true" ]; then
	mkbootimgcmd="$mkbootimgcmd --dt dt.img"
```

buildscript/build_conf/joonlte/build_conf.joonlte_eur_open
```sh
[build-kernel]
type 	= slsi
subtype = exynos7880
arch_name = arm64
target_model = joonlte
model_variant = exynos7880-general_variant
base_defconfigs = exynos7880-base exynos7880-eng exynos7880-userdebug
dtb	= enable 
dtb-list = exynos7880-joonlte_eur_open_00 exynos7880-joonlte_eur_open_01
```


----

#### fdt.c 디바이스 트리 파서  


세가지 관련 함수가 있음.  
>
- setup_machine_fdt(__fdt_pointer);
	초기 board관련 dt 초기화.  
	(참고문서) device_tree.md   
- unflatten_device_tree();
	dtb에 있는 내용을 파싱하여 device_node 구조체 생성및 초기화.  
	(참고문서) device_tree.md    
- of_platform_populate();
	각 platform_device의 device_node연결  
	(참고문서) platform_driver.md    




```c
# asmlinkage __visible void __init start_kernel(void) "init/main.c"
| setup_arch(&command_line);

# void __init setup_arch(char **cmdline_p) "arch/arm64/kernel/setup.c"
| setup_machine_fdt(__fdt_pointer);
|---
| @ phys_addr_t __fdt_pointer __initdata; "__fdt_pointer 란? phy 주소인듯?  device tree blob의"
| 	"__fdt_pointer 주소값은 uboot에서 만들어 전달하는듯??"
| # static void __init setup_machine_fdt(phys_addr_t dt_phys) "arch/arm64/kernel/setup.c"
| | if (!dt_phys || !early_init_dt_scan(phys_to_virt(dt_phys)))
| |---
| | # bool __init early_init_dt_scan(void *params) "drivers/of/fdt.c"
| | | status = early_init_dt_verify(params);
| | | # bool __init early_init_dt_verify(void *params)
| | | | initial_boot_params = params;
| | | "결국 dtb주소임;  커널은 dtb의 파일경로위치를 알고있는것이 아니라 메모리에 있는 주소만 알고있음 -> initial_boot_params값"
| | | "dtb의 내용은 아래 함수들로 parsing하는 듯"
| | | early_init_dt_scan_nodes();
| | | # void __init early_init_dt_scan_nodes(void)
| | | | " Retrieve various information from the /chosen node "
| | | | of_scan_flat_dt(early_init_dt_scan_chosen, boot_command_line);
| | | |---
| | | | # int __init early_init_dt_scan_chosen(unsigned long node, const char *uname,
| | | | | if (depth != 1 || !cmdline || (strcmp(uname, "chosen") != 0 && strcmp(uname, "chosen@0") != 0))
| | | | | early_init_dt_check_for_initrd(node);
| | | | | # static void __init early_init_dt_check_for_initrd(unsigned long node)
| | | | | | prop = of_get_flat_dt_prop(node, "linux,initrd-start", &len);
| | | | | | prop = of_get_flat_dt_prop(node, "linux,initrd-end", &len);
| | | | | p = of_get_flat_dt_prop(node, "bootargs", &l);
| | | | | "arch/arm64/boot/dts/exynos7880-universal7880.dts 내용 
| | | | | 	chosen {
| | | | | 		bootargs = "console=ram,115200 ess_setup=0x46000000 clk_ignore_unused androidboot.hardware=samsungexynos7880 firmware_class.path=/vendor/firmware reserve-fimc=0 androidboot.debug_level=0x4948";
| | | | | 		linux,initrd-start = <0x52000000>;
| | | | | 		linux,initrd-end = <0x521FFFFF>;
| | | | | 	};
| | | | | "
| | | | " Initialize {size,address}-cells info "
| | | | of_scan_flat_dt(early_init_dt_scan_root, NULL);
| | | |---
| | | | # int __init early_init_dt_scan_root(unsigned long node, const char *uname,
| | | | | prop = of_get_flat_dt_prop(node, "#size-cells", NULL);
| | | | | dt_root_size_cells = be32_to_cpup(prop);
| | | | | prop = of_get_flat_dt_prop(node, "#address-cells", NULL);
| | | | | dt_root_addr_cells = be32_to_cpup(prop);
| | | | | "실제로 arch/arm64/boot/dts/exynos7880.dtsi 에 아래와 같은 내용이 있음
| | | | | 	#address-cells = <2>;
| | | | | 	#size-cells = <1>;
| | | | | "
| | | | " Setup memory, calling early_init_dt_add_memory_arch "
| | | | of_scan_flat_dt(early_init_dt_scan_memory, NULL);
| | | |---
| | | | # int __init early_init_dt_scan_memory(unsigned long node, const char *uname,
| | | | | const char *type = of_get_flat_dt_prop(node, "device_type", NULL);
| | | | | reg = of_get_flat_dt_prop(node, "reg", &l);
| | | | | "arch/arm64/boot/dts/exynos7880-universal7880.dts 내용; 메모리니깐 board 관련임
| | | | | 	memory@40000000 {
| | | | | 		device_type = "memory";
| | | | | 		reg = <0x0 0x40000000 0xC0000000>;
| | | | | 	};
| | | | | "
| | | |---
| | dump_stack_set_arch_desc("%s (DT)", of_flat_dt_get_machine_name());
| | # const char * __init of_flat_dt_get_machine_name(void) "drivers/of/fdt.c"
| | | name = of_get_flat_dt_prop(dt_root, "model", NULL);
| | | name = of_get_flat_dt_prop(dt_root, "compatible", NULL);
| | | "arch/arm64/boot/dts/exynos7880-universal7880.dts 파일 내용중 아래 property파싱함
| | | 보드 기본 정보임
| | | 	model = "Exynos 7880 Universal Board";
| | | 	compatible = "samsung,exynos7880", "samsung,universal7880";
| | | "
| | # void __init dump_stack_set_arch_desc(const char *fmt, ...) "kernel/printk/printk.c"
----
| | of_scan_flat_dt(early_init_dt_scan_ect, NULL);
----
| | # int __init of_scan_flat_dt(int ( *it)(unsigned long node,  "drivers/of/fdt.c"
|---
| unflatten_device_tree();
|---
| " unflatten_device_tree - create tree of device_nodes from flat blob"
| # void __init unflatten_device_tree(void) "drivers/of/fdt.c"

```

- `(참고)` of_get_flat_dt_prop() 함수 분석

- `(참고)` __initdata란?
아래와 같이 선언된 변수 __fdt_pointer뒤에 있는 __initdata의 의미는?

phys_addr_t __fdt_pointer __initdata;    "arch/arm64/kernel/setup.c"
원래 전역변수는 .bss영역에 초기화되는데(0으로 초기화 되어있음)
변수뒤에 __initdata를 명시하면 .data영역으로 초기화 되지 않은상태로 선언할 수 있음.

아래는 include/linux/init.h 의 주석내용임. 
>
```txt
For uninitialized global variables:
You should add __initdata after the variable name, e.g.:

static int init_variable __initdata;

Tagging an uninitialized global variable "__initdata" will cause
the compiler to move it from .bss to .data.
```

----

- dtb로 부터 device_node생성하기 unflatten_device_tree()

```c
# asmlinkage __visible void __init start_kernel(void) "init/main.c"
| setup_arch(&command_line);
| # void __init setup_arch(char **cmdline_p) "arch/arm64/kernel/setup.c"
| | ...
| | setup_machine_fdt(__fdt_pointer);
| | ...
| | unflatten_device_tree();
---
" unflatten_device_tree - create tree of device_nodes from flat blob"
# void __init unflatten_device_tree(void) "drivers/of/fdt.c"
| __unflatten_device_tree(initial_boot_params, &of_allnodes,
      			early_init_dt_alloc_memory_arch);
|---
| " initial_boot_params: dtb 주소,  of_allnodes : 모든 device_node의 root"
| # static void __unflatten_device_tree(void *blob,
      		     struct device_node **mynodes,
      		     void * ( *dt_alloc)(u64 size, u64 align))
| | struct device_node **allnextp = mynodes;
| | mem = dt_alloc(size + 4, __alignof__(struct device_node));
| | unflatten_dt_node(blob, mem, &start, NULL, &allnextp, 0);
| |---
| | " unflatten_dt_node - Alloc and populate a device_node from the flat tree"
| | # static void * unflatten_dt_node(void *blob, ..., struct device_node *dad,
		struct device_node ***allnextpp, unsigned long fpsize)
| | | struct device_node *np;
| | | np = unflatten_dt_alloc(&mem, sizeof(struct device_node) + allocl,
| | | "np 에 device_node구조체 alloc"
| | | **allnextpp = np;
| | | *allnextpp = &np->allnext;
| | | np->parent = dad;
| | | while ( *poffset > 0 && depth > old_depth)
| | | 	mem = unflatten_dt_node(blob, mem, poffset, np, allnextpp, fpsize);
| | | 	"np를 생성 및 초기화해서 다시 재귀함수의 dad로 전달,
| | | 	allnextpp는 np->allnext 포인터를 가리키는 포인터"
| |---
|---
| of_alias_scan(early_init_dt_alloc_memory_arch); "aliases, chosen노드 스캔"

```






----
