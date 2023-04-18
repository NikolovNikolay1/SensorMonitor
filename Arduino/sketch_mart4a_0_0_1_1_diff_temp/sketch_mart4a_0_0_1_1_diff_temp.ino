#include <Adafruit_BusIO_Register.h>
#include <Adafruit_I2CDevice.h>
#include <Adafruit_I2CRegister.h>
#include <Adafruit_SPIDevice.h>


// !!!!!!!!!! Arduino библиотека Serial  https://all-arduino.ru/biblioteki-arduino/arduino-biblioteka-serial/

#include <Adafruit_ADS1X15.h> // Библиотека для работы с модулями ADS1115 и ADS1015
#include <Wire.h> // Библиотека для работы с шиной I2C
#include <AHTxx.h> // библиотека сенсора тампературы и влажности для ATH25

unsigned long time_c;
unsigned long time_0;
unsigned long time_0_AHT;
unsigned long time_AHT;

unsigned int b;
String ver ="0.0.0.2";
unsigned int val;
byte sinhron =123;
byte cod_signal;
byte nDevices_I2C=0;

float k_ads1015;

int16_t float_0;
int16_t float_1;

// наличие сенсоров
//boolean ADS1115_present_48 = false;
//boolean AHT25_present_38 = false;
//

int c=0;

// #include <adafruit_ads1015.h> 
Adafruit_ADS1115 ads1015; //Здесь необходимо указать адрес устройства   (0x48)
AHTxx aht25(AHTXX_ADDRESS_X38, AHT2x_SENSOR);

struct Base_struct_float {   // == 11 byte
  
  int name_tag = 0 ; // 2 byte   (- TO arduino; + FROM arduino; 0 - unAssign
  unsigned long time = 0; // 4 byte
  float val = 0;  // 4 byte  
  char crc ;             // 1 byte
  
};

struct Base_struct_float_diff_temperature {   // == 23 byte
  
  int name_tag = 0 ; // 2 byte   (- TO arduino; + FROM arduino; 0 - unAssign
  unsigned long time = 0; // 4 byte
  float val_0 = 0;  // 4 byte  
  float val_1 = 0;  // 4 byte  
  float val_R_0 = 0;  // 4 byte  
  float val_R_1 = 0;  // 4 byte
  char crc ;             // 1 byte
  
};


struct Base_struct_float_humidity_temper {   // == 15 byte
  
  int name_tag = 0 ; // 2 byte   (- TO arduino; + FROM arduino; 0 - unAssign
  unsigned long time = 0; // 4 byte
  float val_0 = 0;  // 4 byte  
  float val_1 = 0;  // 4 byte  
  char crc ;             // 1 byte
  
};

struct Devices {
  // наличие сенсоров
  // authorization

  boolean ADS1115_present_48=false;
  boolean AHT25_present_38=false;
  int nDevices_I2C=0;
};

  Base_struct_float_diff_temperature buf_float_temperature;
  Base_struct_float_humidity_temper buf_hum_temp_x38;
  
  Devices Devices_presents; // наличие
  Devices Devices_authorization; // разрешение
  
void setup() {
  //разрешены. но наличие проверяется
  Devices_authorization.ADS1115_present_48=true;
  Devices_authorization.AHT25_present_38=true;
  
  // put your setup code here, to run once:
  Serial.begin(2000000); //   115200
//  Serial.begin(9600); 
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
  
 Devices_presents=scaner_addres_I2C_device();
// Serial.print("done\n  finde ");
//        Serial.println(Devices_presents.nDevices_I2C);
//  delay(5000);
 

    buf_hum_temp_x38.name_tag=8;
    buf_hum_temp_x38.val_0=0;
    buf_hum_temp_x38.val_1=0;
    buf_hum_temp_x38.time = 0;
    buf_hum_temp_x38.crc=0;
    
  time_0=  micros (); //millis()
  time_0_AHT = millis();
  
  Serial.flush();
  analogReference(INTERNAL); //1.1V
  //pinMode(1,INPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  

  buf_float_temperature.name_tag=7;
  float_0 = ads1015.readADC_Differential_0_1(); // Измеряем значение АЦП на канало 0-1
  float_1 = ads1015.readADC_Differential_2_3(); // Измеряем значение АЦП на канало 2-3
    
  time_c = micros()- time_0;
  buf_float_temperature.time = time_c;// 77; 
 
   // Расчёт напряжения
  buf_float_temperature.val_0 =1.1;// float_0*k_ads1015/1000; //  c;
  buf_float_temperature.val_1 = float_1*k_ads1015;//k_ads1015;
  buf_float_temperature.crc = 0; // ? crc8_bytes((byte*)&buf, sizeof(buf) - 1);

//  float val = analogRead(1);    // считываем напряжение с аналогового входа
  buf_float_temperature.val_R_0 =1.2;//*k_ads1015*1000/47; //val/1024 *1.1; //mA
  buf_float_temperature.val_R_1 =float_0*k_ads1015; //val/1024 *1.1/47*1000;

  //sinhron=123;
  //Serial.write((byte*)&sinhron, sizeof(sinhron));

 // if (Serial.available() ) { 
 
  
  cod_signal=7;
  Serial.write((byte*)&cod_signal, sizeof(cod_signal));
  
  
  //Serial.print(cod_signal);
 
 // }
//  if (Serial.available() ) { 
  Serial.write((byte*)&buf_float_temperature, sizeof(buf_float_temperature));
  
  time_AHT = millis()- time_0_AHT;
  if( (Devices_authorization.AHT25_present_38==true) and (Devices_presents.AHT25_present_38==true) and (time_AHT>=1000) )
  {
    read_sensors_ATH_x38();  // чтение и передача
    time_0_AHT = millis();
  } 

  c=c+1;
//  Serial.flush();
 
}

void serialEvent(){

//  statements
//Автоматически вызывается, когда есть доступные данные.
}

void read_sensors_ATH_x38()
{
    float T = aht25.readTemperature();
    float H = aht25.readHumidity();
    buf_hum_temp_x38.name_tag=8;
    buf_hum_temp_x38.val_0=T;
    buf_hum_temp_x38.val_1=H;
    buf_hum_temp_x38.time = time_c;
    buf_hum_temp_x38.crc=0;
    cod_signal=8;
    Serial.write((byte*)&cod_signal, sizeof(cod_signal));
    Serial.write((byte*)&buf_hum_temp_x38, sizeof(buf_hum_temp_x38));
}

Devices scaner_addres_I2C_device(){
  byte error, address;
  
  Devices my_Devices;
  my_Devices.ADS1115_present_48=false;
  my_Devices.AHT25_present_38=false;
  my_Devices.nDevices_I2C=0;
 
 
    for(address = 1; address < 127; address++ ){
        Wire.beginTransmission(address);
        error = Wire.endTransmission();
 
        if (error == 0){
            //Serial.print("I2C device found at address 0x");
            //if (address < 16)
            //    Serial.print("0");
            //Serial.print(address,HEX);
            //Serial.println(" !");
            if (address == 0x48) {
              my_Devices.ADS1115_present_48 = true;
               my_Devices.nDevices_I2C++;
             // Serial.print(address,HEX);
             // delay(1000);
            };
            if (address == 0x38) {
              my_Devices.AHT25_present_38 = true;
             // Serial.print(address,HEX);
               my_Devices.nDevices_I2C++;
             // delay(1000);
            };
           
        }
        else if (error == 4) {
            Serial.print("Unknow error at address 0x");
          //  if (address < 16)
          //      Serial.print("0");
            Serial.println(address,HEX);
        } 
    }
    if (my_Devices.nDevices_I2C == 0)
        Serial.println("No I2C devices found\n");
    else {
        Serial.print("done\n  finde ");
        Serial.println(my_Devices.nDevices_I2C);
    }
 
    delay(1000);
   return my_Devices;
}
