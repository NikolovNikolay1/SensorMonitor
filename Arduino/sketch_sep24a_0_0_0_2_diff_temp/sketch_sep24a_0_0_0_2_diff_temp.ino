#include <Adafruit_BusIO_Register.h>
#include <Adafruit_I2CDevice.h>
#include <Adafruit_I2CRegister.h>
#include <Adafruit_SPIDevice.h>

// !!!!!!!!!! Arduino библиотека Serial  https://all-arduino.ru/biblioteki-arduino/arduino-biblioteka-serial/

#include <Adafruit_ADS1X15.h> // Библиотека для работы с модулями ADS1115 и ADS1015
#include <Wire.h> // Библиотека для работы с шиной I2C

unsigned long time_c;
unsigned long time_0;
unsigned int b;
String ver ="0.0.0.2";
unsigned int val;
byte sinhron =123;
byte cod_signal;

float k_ads1015;

int16_t float_0;
int16_t float_1;

int c=0;

// #include <adafruit_ads1015.h> 
Adafruit_ADS1115 ads1015; //Здесь необходимо указать адрес устройства   (0x48)


struct Base_struct_float {   // == 11 byte
  
  int name_tag = 0 ; // 2 byte   (- TO arduino; + FROM arduino; 0 - unAssign
  unsigned long time = 0; // 4 byte
  float val = 0;  // 4 byte  
  char crc ;             // 1 byte
  
};

struct Base_struct_float_diff_temperature {   // == 11 byte
  
  int name_tag = 0 ; // 2 byte   (- TO arduino; + FROM arduino; 0 - unAssign
  unsigned long time = 0; // 4 byte
  float val_0 = 0;  // 4 byte  
  float val_1 = 0;  // 4 byte  
  float val_R_0 = 0;  // 4 byte  
  float val_R_1 = 0;  // 4 byte
  char crc ;             // 1 byte
  
};

  Base_struct_float_diff_temperature buf_float_temperature;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(2000000); //   115200
  Serial.setTimeout(100);

  analogReference (INTERNAL); // 1,1В -макс  http://robotosha.ru/karta-sajta/handbook/analogreference
     // работа с АЦП Ардуино  http://robotosha.ru/arduino/analog-measurements-arduino.html
  
  
  // Установка коэффициента усиления 2/3
  ads1015.setGain(GAIN_SIXTEEN);
  k_ads1015=0.0078125;

  // ВОЗМОЖНЫЕ ВАРИАНТЫ УСТАНОВКИ КУ:
  // ads.setGain(GAIN_TWOTHIRDS); | 2/3х | +/-6.144V | 1bit = 0.1875mV    |
  // ads.setGain(GAIN_ONE);       | 1х   | +/-4.096V | 1bit = 0.125mV     |
  // ads.setGain(GAIN_TWO);       | 2х   | +/-2.048V | 1bit = 0.0625mV    |
  // ads.setGain(GAIN_FOUR);      | 4х   | +/-1.024V | 1bit = 0.03125mV   |
  // ads.setGain(GAIN_EIGHT);     | 8х   | +/-0.512V | 1bit = 0.015625mV  |
  // ads.setGain(GAIN_SIXTEEN);   | 16х  | +/-0.256V | 1bit = 0.0078125mV |

  ads1015.begin(); // Инициализация модуля ADS1115
  
  

  Base_struct_float_diff_temperature buf_float_temperature;
  
  time_0=  micros (); //millis()
  
  
  Serial.flush();
}

void loop() {
  // put your main code here, to run repeatedly:
  

  buf_float_temperature.name_tag=7;
  float_0 = ads1015.readADC_Differential_0_1(); // Измеряем значение АЦП на канало 0-1
  float_1 = ads1015.readADC_Differential_2_3(); // Измеряем значение АЦП на канало 2-3
    
  time_c = micros()- time_0;
  buf_float_temperature.time = time_c;// 77; 
 
   // Расчёт напряжения
  buf_float_temperature.val_0 = float_0*k_ads1015/1000; //  c;
  buf_float_temperature.val_1 = float_1*k_ads1015/1000;
  buf_float_temperature.crc = 0; // ? crc8_bytes((byte*)&buf, sizeof(buf) - 1);

  val = analogRead(0);    // считываем напряжение с аналогового входа
  buf_float_temperature.val_R_0 = val/1024 *1.1;
  buf_float_temperature.val_R_1 =0;

  sinhron=123;
  //if (Serial.available() ) { 
  Serial.write((byte*)&sinhron, sizeof(sinhron));
 // }
 // if (Serial.available() ) { 
  cod_signal=7;
  Serial.write((byte*)&cod_signal, sizeof(cod_signal));
  //Serial.print(cod_signal);
 
 // }
//  if (Serial.available() ) { 
  Serial.write((byte*)&buf_float_temperature, sizeof(buf_float_temperature));
//  Serial.println(buf_float_temperature);
//  }
  c=c+1;
//  Serial.flush();
 
}

void serialEvent(){

//  statements
//Автоматически вызывается, когда есть доступные данные.
}
