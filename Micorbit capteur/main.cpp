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
#include <tsl256x.h>
#include <ssd1306.h>
#include <bme280.h>
#include <aes.hpp>


// Define the AES key
const uint8_t my_AES_key[16] = "+1Corenthiens13";


// Function to convert a character array to a uint8_t array
void convertion_en_uint(char* in, int size, uint8_t* out) {
    for (int i = 0; i < size; i++) {
        out[i] = (uint8_t)in[i];
    }
}


// Function to convert a uint8_t array to a character array
void convertion_en_char(uint8_t* in, int size, char* out) {
    for (int i = 0; i < size; i++) {
        out[i] = (char)in[i];
    }
    out[size] = '\0';
}


// Function for encryption using AES
ManagedString encryption(ManagedString src){
    uint8_t data[16];
    char received[17];
    for(int i=0; i<16; i++){
        received[i] = src.charAt(i);
    }

    // Convert characters to uint8_t array,
    convertion_en_uint (received,16,data);
    
    // Then encrypt the data using AES in ECB mode back to characters
    struct AES_ctx ctx;
    AES_init_ctx(&ctx, my_AES_key);
    AES_ECB_encrypt(&ctx, data);
    convertion_en_char(data,16, received);
    return ManagedString(received);
}


// Function for decryption using AES
ManagedString decryption(ManagedString src){
    uint8_t data[16];
    char received[17];
    for (int i = 0; i < 16; i++) {
        received[i] = src.charAt(i);
    }
        
    // Convert characters to uint8_t array,
    convertion_en_uint (received,16,data);
    
    // Then decrypt the data using AES in ECB mode as a ManagedString
    struct AES_ctx ctx;
    AES_init_ctx(&ctx, my_AES_key);
    AES_ECB_decrypt(&ctx, data);
    convertion_en_char(data,16, received);
    return ManagedString(received);
}


// Global variables
MicroBit uBit;
bool ordre1;


// Function for handling received radio data
void onData(MicroBitEvent)
{
    // Receive and decrypt
    
    ManagedString s = uBit.radio.datagram.recv();
    ManagedString s_decrypt = decryption(s);

    // Check if the decrypted data starts with "1857"
    if (s_decrypt.substring(0,4) == "1857"){
        // Check the order
        if (s_decrypt.substring(5,2)== "TL")
        {
            ordre1 = true;
        }
        else if (s_decrypt.substring(5,2)=="LT")
        {
            ordre1 = false;
        }
    }
}


int main()
{
    // Micro:bit initialization
    uBit.init();

    // I2C setup for sensors
    MicroBitI2C i2c(I2C_SDA0,I2C_SCL0);
    bme280 bme(&uBit,&i2c);
    tsl256x tsl(&uBit,&i2c);
    
    // Sensor variables
    uint32_t pressure = 0;
    int32_t temp = 0;
    uint16_t humidite = 0;
    uint16_t comb =0;
    uint16_t ir = 0;
    uint32_t lux = 0;

    // Screen setup
    MicroBitPin P0(MICROBIT_ID_IO_P0, MICROBIT_PIN_P0, PIN_CAPABILITY_ALL);
    ssd1306 screen(&uBit, &i2c, &P0);
    
    // Packet buffer for radio transmission and enable
    PacketBuffer packet(20);
    uBit.radio.enable();
    uBit.messageBus.listen(MICROBIT_ID_RADIO, MICROBIT_RADIO_EVT_DATAGRAM, onData);

    
    // Set digital value for P2
    uBit.io.P2.setDigitalValue(1);

    while (1){
        uBit.display.clear();

        // Read temperature, humidity, and pressure
        bme.sensor_read(&pressure, &temp, &humidite);                        
        
        // Compensate temperature and format it for display
        int tmp = bme.compensate_temperature(temp);
        ManagedString temperature = ManagedString(tmp/100) + "." + (tmp > 0 ? ManagedString(tmp%100): ManagedString((-tmp)%100));
        ManagedString displaytemp = "Temp:" + temperature;
        ManagedString displaytemp2 = "Temp:" + temperature +"C";
        
        // Format data
        tsl.sensor_read(&comb, &ir, &lux);        
        ManagedString displaylux = "Lux:" + ManagedString((int)lux);

        // Print data
        //uBit.serial.printf("\n\r%s",displaytemp.toCharArray());
        //uBit.serial.printf("\n\r%s",displaylux.toCharArray());
        //uBit.sleep(1000);

        // Display temperature and lux data based on the order 
        screen.display_line(0,0,"Donnees : ");
        screen.display_line(1,0,"                                      ");
        screen.display_line(2,0,"                                      ");

        if (ordre1 == true)
        {
            
            screen.display_line(1,0,displaytemp2.toCharArray());
            screen.display_line(2,0,displaylux.toCharArray());
        }
        else
        {
            screen.display_line(1,0,displaylux.toCharArray());
            screen.display_line(2,0,displaytemp2.toCharArray());
        }

        // Uptdate the screen 
        screen.update_screen();
        uBit.sleep(5);

        // Encrypt and send temperature data over the radio
        ManagedString s2 = "1857:"+displaytemp+"\n        ";
        ManagedString s2_encode =encryption(s2);
        memcpy(packet.getBytes(),s2_encode.toCharArray(),20);
        uBit.radio.datagram.send(packet);
        uBit.sleep(5);

        // Encrypt and send lux data over the radio
        ManagedString s3 = "1857:"+displaylux+"\n          ";
        ManagedString s3_encode =encryption(s3);
        memcpy(packet.getBytes(),s3_encode.toCharArray(),20);
        uBit.radio.datagram.send(packet);
    }

    // Release fiber
    release_fiber();

}