#make file
CC = avr-gcc
MCU_NAME = atmega128 #m128
TARGET = main
PROG_TYPE = stk500
PORT_NAME = /dev/ttyUSB0
RM = rm -rf

$(TARGET):$(TARGET).c
	    $(CC) -mmcu=$(MCU_NAME) -o $@.o $^
		   avr-objcopy -O ihex -R .eeprom $@.o $(TARGET).hex
			  avrdude -p $(MCU_NAME) -c $(PROG_TYPE) -P $(PORT_NAME) -U flash:w:$(TARGET).hex:i

clean:
$(RM) $(TARGET).hex $(TARGET).o

