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
