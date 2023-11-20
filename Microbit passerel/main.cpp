/*
The MIT License (MIT)

Copyright (c) 2016 British Broadcasting Corporation.
This software is provided by Lancaster University by arrangement with the BBC.

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
*/
#include <MicroBit.h>
#include <aes.hpp>

//encryption Key
const uint8_t my_AES_key[16] = "+1Corenthiens13";

// Convert Function character chart in uint8_t chart
void convertion_en_uint(char* in, int size, uint8_t* out) {
    for (int i = 0; i < size; i++) {
        out[i] = (uint8_t)in[i];
    }
}

// Convert Function  uint8_t chart in character chart
void convertion_en_char(uint8_t* in, int size, char* out) {
    for (int i = 0; i < size; i++) {
        out[i] = (char)in[i];
    }
    out[size] = '\0';
}

// Encryption Function character string ManagedString in use AES Mode
ManagedString encryption(ManagedString src){
    uint8_t data[16];
    char received[17];
    for(int i=0; i<16; i++){
        received[i] = src.charAt(i);
    }
    convertion_en_uint (received,16,data);
    
    struct AES_ctx ctx;
    AES_init_ctx(&ctx, my_AES_key);
    AES_ECB_encrypt(&ctx, data);
    
    convertion_en_char(data,16, received);
    return ManagedString(received);
}

// Decipher Function character string  ManagedString in use AES Mode
ManagedString decryption(ManagedString src){
    uint8_t data[16];
    char received[17];
    for (int i = 0; i < 16; i++) {
        received[i] = src.charAt(i);
    }
    convertion_en_uint (received,16,data);
    
    struct AES_ctx ctx;
    AES_init_ctx(&ctx, my_AES_key);
    AES_ECB_decrypt(&ctx, data);

    convertion_en_char(data,16, received);
    return ManagedString(received);
}

MicroBit uBit;

// Event handler for receiving radio datagrams
void onData(MicroBitEvent)
{
    ManagedString s = uBit.radio.datagram.recv();
    ManagedString s_decrypt = decryption(s);
    if (s_decrypt.substring(0,4) == "1857"){
        uBit.serial.send(s_decrypt);
    }
}

int main()
{
    // Initializing the execution of the micro:bit.
    uBit.init();
    uBit.radio.enable();
    uBit.messageBus.listen(MICROBIT_ID_RADIO, MICROBIT_RADIO_EVT_DATAGRAM, onData);
    while(1)
    {
        ManagedString data_read_serial = uBit.serial.read(7);

        if (data_read_serial == "1857:TL"){
            ManagedString s2 ="1857:TL\n";

            ManagedString s2_encr = encryption(s2);
            // Create a packet to send encrypted data
            PacketBuffer packet(s2_encr.length());
            memcpy(packet.getBytes(), s2_encr.toCharArray(), s2_encr.length());
            uBit.radio.datagram.send(packet);
        }
        else if (data_read_serial == "1857:LT"){
            ManagedString s2 ="1857:LT\n";
            ManagedString s2_encr = encryption(s2);
            // Create a packet to send encrypted data
            PacketBuffer packet(s2_encr.length());
            memcpy(packet.getBytes(), s2_encr.toCharArray(), s2_encr.length());
            uBit.radio.datagram.send(packet);
        }
    }
}



