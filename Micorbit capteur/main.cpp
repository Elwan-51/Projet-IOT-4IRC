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


const uint8_t my_AES_key[16] = "+1Corenthiens13";


void convertion_en_uint(char* in, int size, uint8_t* out) {
    for (int i = 0; i < size; i++) {
        out[i] = (uint8_t)in[i];
    }
}

void convertion_en_char(uint8_t* in, int size, char* out) {
    for (int i = 0; i < size; i++) {
        out[i] = (char)in[i];
    }
    out[size] = '\0';
}

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

//Variables globales
MicroBit uBit;
bool ordre1;
//Fonction pour la reception des datas
void onData(MicroBitEvent)
{

    ManagedString s = uBit.radio.datagram.recv();
    ManagedString s_decrypt = decryption(s);
    if (s_decrypt.substring(0,4) == "1857"){
        //Bolléen permettant l'affichage LT ou TL
        if (s_decrypt.substring(5,2)== "tl")
        {
            ordre1 = true;
        }
        else if (s_decrypt.substring(5,2)=="lt")
        {
            ordre1 = false;
        }
    }
}


int main()
{
    // Initialisations
    uBit.init();
    MicroBitI2C i2c(I2C_SDA0,I2C_SCL0);
    bme280 bme(&uBit,&i2c);
    uint32_t pressure = 0;
    int32_t temp = 0;
    uint16_t humidite = 0;
    tsl256x tsl(&uBit,&i2c);
    uint16_t comb =0;
    uint16_t ir = 0;
    uint32_t lux = 0;
    MicroBitPin P0(MICROBIT_ID_IO_P0, MICROBIT_PIN_P0, PIN_CAPABILITY_ALL);
    ssd1306 screen(&uBit, &i2c, &P0);
    PacketBuffer packet(20);
        uBit.io.P2.setDigitalValue(1);
    uBit.radio.enable();
    uBit.messageBus.listen(MICROBIT_ID_RADIO, MICROBIT_RADIO_EVT_DATAGRAM, onData);
    //Boucle while (code dedans)
    while (1){
        
        //Initialisation
        uBit.display.clear();

        //Temperature
        bme.sensor_read(&pressure, &temp, &humidite);        
        int tmp = bme.compensate_temperature(temp);
        ManagedString temperature = ManagedString(tmp/100) + "." + (tmp > 0 ? ManagedString(tmp%100): ManagedString((-tmp)%100))+" ";
        ManagedString displaytemp = "Temp:" + temperature;
        ManagedString displaytemp2 = "Temp:" + temperature +"C";
        uBit.serial.printf("\n\r%s",displaytemp.toCharArray());

        //Luminosité
        tsl.sensor_read(&comb, &ir, &lux);        
        ManagedString displaylux = "Lux:" + ManagedString((int)lux);
        uBit.serial.printf("\n\r%s",displaylux.toCharArray());

        //Sleep
        uBit.sleep(1000);

        //Affichage
        screen.display_line(0,0,"Donnees : ");
        if (ordre1 == true)
        {
            //Affichage des valeurs selon l'ordre 1
            screen.display_line(1,0,displaytemp2.toCharArray());
            screen.display_line(2,0,displaylux.toCharArray());
        }
        else
        {
            //Affichage des valeurs selon l'ordre 2
            screen.display_line(1,0,displaylux.toCharArray());
            screen.display_line(2,0,displaytemp2.toCharArray());
        }
        screen.update_screen();

        //Envoie des données
        uBit.sleep(5);
        ManagedString s2 = "1857:"+displaytemp+"\n";
        ManagedString s2_encode =encryption(s2);
        memcpy(packet.getBytes(),s2_encode.toCharArray(),20);
        uBit.radio.datagram.send(packet);
        uBit.sleep(5);
        ManagedString s3 = "1857:"+displaylux+"\n";
        ManagedString s3_encode =encryption(s3);
        
        //encode_str(&s);
        memcpy(packet.getBytes(),s3_encode.toCharArray(),20);
        uBit.radio.datagram.send(packet);
        //uBit.radio.datagram.send("1857:"+displaylux+"\n");

    }

    release_fiber();

}