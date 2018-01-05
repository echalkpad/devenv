
### uevent 란?

udev데몬이 kernel(driver) 로 부터 받는 이벤트.
udevd 가 실제로 드라이버에 해당하는 /dev/ 아래 디바이스파일을 생성하기때문에 중요.

커널에서 디바이스가 detect되면 sysfs에 등록이 되고 유져공간의 /sys/ 아래 노드생성됨.
그뒤 커널은 udevd 에 uevent를 날리고 udevd가 /sys/의 파일을 참고하여 /dev/에 디바이스 파일 생성.


cat /sys/devices/something_device/uevent
위 커맨드를 입력하면 내용이 나온다.


### 관련 코드 분석.  

참고링크 : http://egloos.zum.com/furmuwon/v/11024590  




```c
# static void __init do_basic_setup(void) "init/main.c"
| driver_init();
| # void __init driver_init(void)
| | platform_bus_init();
| | # int __init platform_bus_init(void)
| | | error = device_register(&platform_bus);
| | | # int device_register(struct device *dev)
| | | | device_initialize(dev);
| | | | return device_add(dev);
---
| " 위 말고도 다양한 경로에서 device_add가 호출됨"
# int device_add(struct device *dev) "drivers/base/core.c"
| error = device_create_file(dev, &dev_attr_uevent); "sysfs노드를 만듬"
|---
| # int device_create_file(struct device *dev,
		       const struct device_attribute *attr)
| | error = sysfs_create_file(&dev->kobj, &attr->attr);
| | # static inline int __must_check sysfs_create_file(struct kobject *kobj, "include/linux/sysfs.h"
| | | return sysfs_create_file_ns(kobj, attr, NULL);
| | | # int sysfs_create_file_ns(struct kobject *kobj, const struct attribute *attr, "fs/sysfs/file.c"
| | | | return sysfs_add_file_mode_ns(kobj->sd, attr, false, attr->mode, ns);
| | | | # int sysfs_add_file_mode_ns(struct kernfs_node *parent,
| | | | | kn = __kernfs_create_file(parent, attr->name, mode, size, ops,
				  (void *)attr, ns, true, key);
| | | | | # struct kernfs_node *__kernfs_create_file(struct kernfs_node *parent, "fs/kernfs/file.c"
| | | | | "kernfs는 sysfs를 위한 virtual filesystem 이라고함. 참고 링크: http://www.phoronix.com/scan.php?px=MTU3NzQ&page=news_item"

|---
| "udevd에 uevent를 날리는 함수"
| kobject_uevent(&dev->kobj, KOBJ_ADD);


```



sysfs에서노 uevent날리는 store함수가 있음.

```c
static ssize_t bus_uevent_store(struct bus_type *bus,
				const char *buf, size_t count)
{
	enum kobject_action action;

	if (kobject_action_type(buf, count, &action) == 0)
		kobject_uevent(&bus->p->subsys.kobj, action);
	return count;
}
static BUS_ATTR(uevent, S_IWUSR, NULL, bus_uevent_store);

"그리고 bus_register에서 sysfs등록"
# int bus_register(struct bus_type *bus)
| retval = bus_create_file(bus, &bus_attr_uevent);

```


이따가 찾아보기
int bus_add_driver(struct device_driver *drv)





# 순서

커널부팅중 driver등록시 sysfs 에 uevent파일 생성. 모든 sysfs마다 uevent파일 있음.

부팅 이후 android platform에서 deivce_init()할때 ueventd 가 uevent파일을
파악해서 /dev/* 파일 생성함.

