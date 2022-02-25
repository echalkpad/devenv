

## device_create() 가 어떻게 sysfs 경로?노드?를 만드나?
	switch_device = sec_device_create(NULL, "switch");


```c
# static int __init muic_notifier_init(void) "drivers/muic/muic_notifier.c"
| switch_device = sec_device_create(NULL, "switch");

| # struct device *sec_device_create(void *drvdata, const char *fmt) "drivers/staging/samsung/sec_sysfs.c"
| | dev = device_create(sec_class, NULL, atomic_inc_return(&sec_dev), drvdata, fmt);
| | @ sec_class = class_create(THIS_MODULE, "sec"); "참고 sec_class_create() 에서 sec class 생성"

| | # struct device *device_create(struct class *class, struct device *parent,
			     dev_t devt, void *drvdata, const char *fmt, ...) "drivers/base/core.c"
| | | dev = device_create_vargs(class, parent, devt, drvdata, fmt, vargs);

"/* device_create_vargs - creates a device and registers it with sysfs */"
| | | # struct device *device_create_vargs(struct class *class, struct device *parent,
				   dev_t devt, void *drvdata, const char *fmt, va_list args)
| | | | return device_create_groups_vargs(class, parent, devt, drvdata, NULL,
					  fmt, args);
| | | | # device_create_groups_vargs(struct class *class, struct device *parent,
| | | | | dev = kzalloc(sizeof(*dev), GFP_KERNEL);				*) 
| | | | | dev->class = class;
| | | | | dev->parent = parent;
| | | | | dev_set_drvdata(dev, drvdata); "driver_data 를 여기서 연결해도됨"
| | | | | retval = kobject_set_name_vargs(&dev->kobj, fmt, args); "kobj->name 을 fmt로 초기화"
| | | | | retval = device_add(dev);

| | | | | # int device_add(struct device *dev)
| | | | | | error = kobject_add(&dev->kobj, dev->kobj.parent, NULL);
| | | | | | error = device_create_file(dev, &dev_attr_uevent); "uevent 생성?"
| | | | | | # int device_create_file(struct device *dev,
| | | | | | | error = sysfs_create_file(&dev->kobj, &attr->attr);
| | | | | | | # int sysfs_create_file_ns(struct kobject *kobj, const struct attribute *attr, "fs/sysfs/file.c"
| | | | | | | | return sysfs_add_file_mode_ns(kobj->sd, attr, false, attr->mode, ns);
| | | | | | | | # int sysfs_add_file_mode_ns(struct kernfs_node *parent,
| | | | | | | | | kn = __kernfs_create_file(parent, attr->name, mode, size, ops,
				  (void *)attr, ns, true, key);
| | | | | | | | | # struct kernfs_node *__kernfs_create_file(struct kernfs_node *parent, "fs/kernfs/file.c"
| | | | | | | | | | struct kernfs_node *kn;
| | | | | | | | | | kn->attr.ops = ops;
| | | | | | | | | | rc = kernfs_add_one(kn);
| | | | | | | | | | # int kernfs_add_one(struct kernfs_node *kn) "fs/kernfs/dir.c"
| | | | | | | | | | | ret = kernfs_link_sibling(kn);
| | | | | | | | | | | kernfs_activate(kn);

| | | | | | error = device_create_file(dev, &dev_attr_dev); "dev/ 생성?"
| | | | | | error = device_create_sys_dev_entry(dev);
| | | | | | devtmpfs_create_node(dev);
| | | | | | error = device_add_class_symlinks(dev);
| | | | | | error = device_add_attrs(dev);
| | | | | | error = bus_add_device(dev);
| | | | | | error = dpm_sysfs_add(dev);
| | | | | | device_pm_add(dev);


```

















## 문제 : dev_get_drvdata(dev) 가 어떤 driver_data를 return하는지 check 해주는 코드가 필요할듯.

device 구조체는 driver_data 멤버가 있는데 이는 각 Device Driver 마다 정의한
구조체를 등록 할 수 있다.
sysfs 노드가 호출될때 이 device 구조체 포인터가 인자로 넘어오는데
dev_get_drvdata(dev) 를 사용하여 driver_data 포인터를 얻어서 원하는 동작에 맞게 사용한다.
리턴되는 구조체 포인터 타입이 정상인지도 판단하지 않고 사용하고 있다.
그래서 Kernel Panic이 발생한 이슈가 있었다. 아래글(내가 메일보냈던내용) 참고.


```c
struct device {
	...
	void	*driver_data;	/* Driver data, set and get with
					   dev_set/get_drvdata */
	...
}
```


아래는 dev_get_drvdata(dev)가 어떤 driver_data를 return 하는지 몰라서 발생한 문제.

--------

문제는 struct device *switch_device구조체의 driver_data 멤버를 
어디서 등록하느냐 입니다.

지금까지는 MUIC 에서 등록하고 있었습니다.

/drivers/muic/s2mu005-muic.c
```c
	dev_set_drvdata(switch_device, muic_data);
```


CL 6565416 이후에
하지만 -- /sys/class/sec/switch/uart_sel 
sysfs node 를 modem_v1으로 옮기기 위하여, 아래와 같이
switch_device의 driver_data를 struct modem_ctrl *mc 로 등록했습니다.

/drivers/misc/modem_v1/modem_ctrl_ss310ap.c
```c
	dev_set_drvdata(switch_device, mc);
```


그러나 그 이후에 muic에서 사용하는 /sys/class/sec/switch/* 
sysfs node의 store 및 show함수에서 문제가 되고 있습니다.
가령 아래의 *muic_data 구조체 포인터에 실제로는 modem_ctrl구조체 포인터가 연결됩니다.
따라서 Kernel Panic이 발생합니다.

/drivers/muic/s2mu005-muic.c
```c
static ssize_t s2mu005_muic_show_adc(struct device *dev,
				      struct device_attribute *attr, char *buf)
{
	struct s2mu005_muic_data *muic_data = dev_get_drvdata(dev);

	mutex_lock(&muic_data->muic_mutex);
	...
}
```


이문제를 해결하기 위하여, Joshua 과제에서는 CL 6573541 로 

/drivers/misc/modem_v1/modem_ctrl_ss310ap.c 의
```patch
- dev_set_drvdata(switch_device, mc); 
```
를 제거한것으로 보입니다만,

해당 CL이 반영된 이후의 문제는 또, 아래의 함수(modem_v1쪽 파일)에서 mc구조체 포인터에
struct s2mu005_muic_data * muic_data 포인터가 등록된다는 점입니다.
아래에서 mc->uart_dir 을 사용하고 있기 때문에, 문제가 발생될것으로 추측됩니다.(Joshua과제)

/drivers/misc/modem_v1/modem_ctrl_ss310ap.c
```c
uart_change_store(struct device *dev, struct device_attribute *attr,
				const char *buf, size_t count)
{
	struct modem_ctl *mc = dev_get_drvdata(dev);
```


따라서 위와같이 단순한 수정으로는 두군데 모두 문제가 발생하고 있으니
어떻게 수정해야할지 논의가 필요할 것같습니다.


------
