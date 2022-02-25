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
