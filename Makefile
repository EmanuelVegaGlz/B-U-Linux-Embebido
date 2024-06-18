SOURCE = main.c
MCU = atmega328p
CC = avr-gcc
PROGRAMMER = usbasp
PRG = main

OBJCOPY = avr-objcopy
OBJDUMP = avr-objdump

clean:
	rm -rf *.o $(PRG)
	rm -rf *.hex

ofile:
	$(CC) $(SOURCE) -o $(PRG) -Wall -Os -mmcu=$(MCU)

text: hex

hex: $(PRG).hex

%.hex:
	$(OBJCOPY) -O ihex $(PRG) $(PRG).hex

all: ofile text

install: clean all
	sudo avrdude -p $(MCU) -c $(PROGRAMMER) -v -U flash:w:$(PRG).hex:i
