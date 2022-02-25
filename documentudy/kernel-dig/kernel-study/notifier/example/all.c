obj-m += noti_reg.o callchain1_reg.o callchain2_reg.o callchain.o
KDIR:=/home/mogin/s3c2440/linux-2.6.33_usb0

.PHONY: clean

all:
	make -C $(KDIR) SUBDIRS=$(PWD) modules

clean:
	make -C $(KDIR) SUBDIRS=$(PWD) clean

#include <linux/module.h>
#include <linux/notifier.h>
#include <asm/kdebug.h>
#include "test_notifier.h"

/* Driver Initialization */
static int __init callchain_init(void)
{
	blocking_notifier_call_chain(&my_noti_chain,100,NULL);
	return 0;
}
static void __exit callchain_exit(void)
{
}

MODULE_LICENSE( "GPL" );
module_init(callchain_init);
module_exit(callchain_exit);

#include <linux/notifier.h>
#include <linux/module.h>
#include <asm/kdebug.h>
#include "test_notifier.h"

int callchain_event_handler1(struct notifier_block *self,
		unsigned long val, void *data);


static struct notifier_block callchain_notifier1 = {
	.notifier_call = callchain_event_handler1,
};

/* User-defined notification event handler */
int callchain_event_handler1(struct notifier_block *self,
		unsigned long val, void *data)
{
	printk("callchain_event_handler1 Val=%ld\n", val);
	return 0;
}

/* Driver Initialization */
	static int __init
callchain1_reg_init(void)
{
	register_test_notifier(&callchain_notifier1);
	/* ... */
	return 0;
}
static void __exit callchain1_reg_exit(void)
{
	unregister_test_notifier(&callchain_notifier1);
}
MODULE_LICENSE( "GPL" );
module_init(callchain1_reg_init);
module_exit(callchain1_reg_exit);

#include <linux/notifier.h>
#include <linux/module.h>
#include <asm/kdebug.h>
#include "test_notifier.h"

int callchain_event_handler2(struct notifier_block *self,
		unsigned long val, void *data);


static struct notifier_block callchain_notifier2 = {
	.notifier_call = callchain_event_handler2,
};

/* User-defined notification event handler */
int callchain_event_handler2(struct notifier_block *self,
		unsigned long val, void *data)
{
	printk("callchain_event_handler2 Val=%ld\n", val);
	return 0;
}

/* Driver Initialization */
	static int __init
callchain1_reg2_init(void)
{
	register_test_notifier(&callchain_notifier2);
	/* ... */
	return 0;
}
static void __exit callchain1_reg2_exit(void)
{
	unregister_test_notifier(&callchain_notifier2);
}
MODULE_LICENSE( "GPL" );
module_init(callchain1_reg2_init);
module_exit(callchain1_reg2_exit);
#include <linux/module.h>
#include <linux/notifier.h>
#include <asm/kdebug.h>
#include "test_notifier.h"


/* User-defined notifier chain implementation */
BLOCKING_NOTIFIER_HEAD(my_noti_chain);
EXPORT_SYMBOL(my_noti_chain);
int register_test_notifier(struct notifier_block *nb)
{
	/* Register a user-defined Notifier */
	return blocking_notifier_chain_register(&my_noti_chain, nb);
}
EXPORT_SYMBOL(register_test_notifier);
int unregister_test_notifier(struct notifier_block *nb)
{
	return blocking_notifier_chain_unregister(&my_noti_chain, nb);
}
EXPORT_SYMBOL(unregister_test_notifier);
MODULE_LICENSE( "GPL" );
#ifndef __TEST_NOTIFIER_H__
#define __TEST_NOTIFIER_H__
#include <linux/module.h>
#include <linux/notifier.h>
#include <asm/kdebug.h>
extern struct blocking_notifier_head my_noti_chain;
extern int register_test_notifier(struct notifier_block *nb);
extern int unregister_test_notifier(struct notifier_block *nb);
#endif
