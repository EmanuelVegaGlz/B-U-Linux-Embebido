#define F_CPU 16000000UL
#include <avr/io.h>
#include <util/delay.h>

const int FCUP=0;

int main(){
    DDRB = (1<<PB1)|(1<<PB2)|(1<<PB3)|(1<<PB4)|(1<<PB5);
    PORTB = 0xFF;
    while(1){
        PORTB = (1<<PB1);
        _delay_ms(1000);
        PORTB &= 0x00;
        PORTB = (1<<PB2);
        _delay_ms(1000);
        PORTB &= 0x00;
        PORTB = (1<<PB3);
        _delay_ms(1000);
        PORTB &= 0x00;
        PORTB = (1<<PB4);
        _delay_ms(1000);
        PORTB &= 0x00;
        PORTB = (1<<PB5);
        _delay_ms(1000);
        PORTB &= 0x00;
        
    }

}
