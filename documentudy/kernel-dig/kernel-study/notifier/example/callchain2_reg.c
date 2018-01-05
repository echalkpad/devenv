
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
