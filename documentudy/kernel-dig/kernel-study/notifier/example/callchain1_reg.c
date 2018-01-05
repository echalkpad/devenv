
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
