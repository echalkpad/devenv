#ifndef __TEST_NOTIFIER_H__
#define __TEST_NOTIFIER_H__
#include <linux/module.h>
#include <linux/notifier.h>
#include <asm/kdebug.h>
extern struct blocking_notifier_head my_noti_chain;
extern int register_test_notifier(struct notifier_block *nb);
extern int unregister_test_notifier(struct notifier_block *nb);
#endif
