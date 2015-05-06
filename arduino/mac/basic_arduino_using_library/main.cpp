#include <Arduino.h>
#define DELAY_TIME	1000

int ledPin =  13;    // LED connected to digital pin 13

void setup() {
	pinMode(ledPin, OUTPUT);
}

void loop() {
	digitalWrite(ledPin, HIGH);	// set the LED on
	delay(DELAY_TIME);		// wait for half a second
	digitalWrite(ledPin, LOW);	// set the LED off
	delay(DELAY_TIME);		// wait for half a second
}

int main(void) {
	init();
	setup();
	for (;;) {
		loop();
	}
}
