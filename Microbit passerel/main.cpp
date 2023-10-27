#include "MicroBit.h"

MicroBit    uBit;
void onData(MicroBitEvent)
{
    ManagedString s = uBit.radio.datagram.recv();
    if (s.substring(0,4) == "1857"){
        uBit.serial.send(s);
        
    }
}
int main()
{
    // Initialise the micro:bit runtime.
    uBit.init();
    uBit.radio.enable();
    uBit.messageBus.listen(MICROBIT_ID_RADIO, MICROBIT_RADIO_EVT_DATAGRAM, onData);

    while(1)
    {
        if (uBit.buttonA.isPressed())
            uBit.radio.datagram.send("1857:tl\n");
    
        else if (uBit.buttonB.isPressed())
            uBit.radio.datagram.send("1857:lt\n");

        uBit.sleep(100);
    }
        
}


