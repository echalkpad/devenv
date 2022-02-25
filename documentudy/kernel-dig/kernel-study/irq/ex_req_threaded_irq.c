/*
 * From :
 * http://www.programmershare.com/2740674/
 */
# include <linux/interrupt.h>
# include <linux/irq.h>
# include <linux/module.h>

MODULE_LICENSE ("GPL");
static int irq = 10; // definition of the middle number

static irqreturn_t irq_handler (int data, void * dev_id)
{
	printk ("<0> The DATA is:% d \ n", data); // Data corresponding interrupt of
	printk ("<0> in the interrupt handler function \ n");
	return IRQ_WAKE_THREAD; // trigger interrupt thread function execution
}

// Custom interrupt thread handling functions
static irqreturn_t irq_thread_fn (int data, void * dev_id)
{
	printk ("<0> The DATA is:% d \ n", data); // Data corresponding interrupt of
	printk ("<0> in the interrupt thread function \ n");
	return IRQ_HANDLED;
}

static int __init request_threaded_irq_init (void)
{
	int result = 0;
	printk ("<0> into request_threaded_irq_init \ n");
	/* Call request_threaded_irq. () Function, irq is the corresponding
	   interrupt number, irq_handler defined interrupt handler, the
	   irq_thread_fn corresponding interrupt thread handling functions,
	   type of IRQF_DISABLED interrupt */

	result = request_threaded_irq (irq, irq_handler, irq_thread_fn, IRQF_DISABLED, "A_New_Device", NULL);
	printk ("<0> the result of the request_threaded_irq is:% d \ n", result); // display the result of the function call
	disable_irq (IRQ); // interrupt unavailable
	enable_irq (IRQ); // enable interrupts trigger the execution of the interrupt handler
	printk ("<0> out request_threaded_irq_init \ n");
	return 0;
}

static void __exit request_threaded_irq_exit (void)
{
	free_irq (IRQ, NULL); // release the application interrupt
		printk ("<0> Goodbye request_threaded_irq \ n");
	return;
}
module_init (request_threaded_irq_init);
module_exit (request_threaded_irq_exit);
