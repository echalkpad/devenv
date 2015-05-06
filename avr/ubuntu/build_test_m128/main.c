#include <avr/io.h>
#include <util/delay.h>

void main(void)
{
	DDRA = 0xff;
	PORTA = 0x00;
	while(1) {
		_delay_ms(5000);
		PORTA = 0xff;
		_delay_ms(5000);
		PORTA = 0x00;
	}

}
