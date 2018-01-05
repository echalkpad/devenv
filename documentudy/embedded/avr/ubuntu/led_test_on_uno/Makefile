#make file
CC = avr-gcc
MCU_NAME = atmega328p
TARGET = led
PROG_TYPE = arduino
#PORT_NAME = /dev/ttyACM0
PORT_NAME = /dev/tty.usbmodem1421
RM = rm -rf

$(TARGET):$(TARGET).c
	$(CC) -Os -DF_CPU=16000000UL -mmcu=$(MCU_NAME) -o $@.o $^
	avr-objcopy -O ihex -R .eeprom $@.o $(TARGET).hex

upload:
	sudo avrdude -p $(MCU_NAME) -c $(PROG_TYPE) -P $(PORT_NAME) -U flash:w:$(TARGET).hex:i

clean:
	$(RM) $(TARGET).hex $(TARGET).o
