#include <xc.h>
#include <stdio.h>
#include <pic18f4520.h>

#pragma config OSC = INTIO67 // Oscillator Selection bits
#pragma config WDT = OFF     // Watchdog Timer Enable bit
#pragma config PWRT = OFF    // Power-up Enable bit
#pragma config BOREN = ON    // Brown-out Reset Enable bit
#pragma config PBADEN = OFF  // Watchdog Timer Enable bit
#pragma config LVP = OFF     // Low Voltage (single -supply) In-Circute Serial Pragramming Enable bit
#pragma config CPD = OFF     // Data EEPROM?Memory Code Protection bit (Data EEPROM code protection off)
#define _XTAL_FREQ 8000000
/*
0   0xf7
1   0x24
2   0xdd
3   0xed
4   0x2e
5   0x6b
6   0xfb
7   0x25
8   0xff
9   0x6f
*/
void main(void)
{
    unsigned char number[] = {0xf7, 0x24, 0xdd, 0xed, 0x2e, 0x6b, 0xfb, 0x25, 0xff, 0x6f};
    ADCON1 = 0X0F;
    OSCCON = 0X60;
    T0CON = 0X07;
    TMR0H = 0XF0;
    TMR0L = 0XBE;
    TRISA = 0;    // output
    TRISD = 0;    // output
    TRISB = 0X01; //  input
    INTCONbits.TMR0IF = 0;
    LATA = number[6];
    LATD = number[0];
    PORTBbits.RB1 = 0;
    while (PORTBbits.RB0 == 1)
        ;
    T0CONbits.TMR0ON = 1;
    int count_time = 60;
    while (1)
    {

        while (!INTCONbits.TMR0IF)
        {
            if (T0CONbits.TMR0ON == 0)
            {
                PORTBbits.RB1 = 0;
            }
            else
            {
                PORTBbits.RB1 = 1;
            }
            
            if (PORTBbits.RB0 == 0)
            {
                if (T0CONbits.TMR0ON == 0)
                {
                    T0CONbits.TMR0ON = 1;
                }
                else
                {
                    T0CONbits.TMR0ON = 0;
                    count_time = 60;
                    LATA = number[6];
                    LATD = number[0];
                }
                __delay_ms(200);
            }
        }
        if (count_time != 0 && T0CONbits.TMR0ON == 1)
        {
            count_time--;
            int dig1 = count_time / 10;
            int dig2 = count_time % 10;
            LATA = number[dig1];
            LATD = number[dig2];
            TMR0H = 0XF0;
            TMR0L = 0XBE;
            INTCONbits.TMR0IF = 0;
        }

        else
        {
            T0CONbits.TMR0ON = 0;
        }
    }

    while (1)
        ;
    return;
}

