#include <Arduino.h>
#include <SoftwareSerial.h>
#define BAUD_RATE	115200

String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete

void serialEvent()
{
	while (Serial.available()) {
		// get the new byte:
		char inChar = (char)Serial.read(); 
		// add it to the inputString:
		inputString += inChar;
		// if the incoming character is a newline, set a flag
		// so the main loop can do something about it:
		if (inChar == '\n') {
			stringComplete = true;
		} 
	}
}

void setup()
{
	Serial.begin(BAUD_RATE);
	Serial.print("Input your character\n\r");
}

void loop()
{
#if 1
	if(Serial.available() > 0) {
		char c = Serial.read();
		Serial.print(c);
	}
#else
	serialEvent();
#endif
}

int main(void) {
	init();
	setup();
	for (;;) {
		loop();
	}
}


