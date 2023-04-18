//#include <AHT10.h>

//#include <AHTxx.h>

#include <AHTxx.h>

//#include <Adafruit_SHT31.h>
#include <Adafruit_ADS1X15.h> // Библиотека для работы с модулями ADS1115 и ADS1015

#include <Wire.h> // Библиотека для работы с шиной I2C
int16_t float_0;
uint8_t readStatus = 0;

// Adafruit_SHT31 sht31 = Adafruit_SHT31();  // создаем объект датчика температуры
AHTxx aht20(AHTXX_ADDRESS_X38, AHT2x_SENSOR);
//AHT10 myAHT20(AHT10_ADDRESS_0X38, AHT20_SENSOR);
Adafruit_ADS1115 ads1015; //Здесь необходимо указать адрес устройства   (0x48)

void setup() {
  // put your setup code here, to run once:
{
   Serial.begin(9600);                             // Открываем последовательную связь, на скорости 9600 
   //sht31.begin(0x44);                              // Инициализация датчик, с адресом 0х44
  ads1015.setGain(GAIN_SIXTEEN);
  float k_ads1015=0.0078125;   
 while (aht20.begin()!= true)
  {
    Serial.println(F("AHT20 not connected or fail to load calibration coefficient")); //(F()) save string to flash & keeps dynamic memory free
    delay(500);
  }
  Serial.println(F("AHT20 OK"));
 while (ads1015.begin()!= true)
 // Инициализация модуля ADS1115
{
    Serial.println(F("ADS1115 not connected")); //(F()) save string to flash & keeps dynamic memory free
    delay(500);
}
    byte error, address;
    int nDevices;
 
    Serial.println("Scanning...");
 
    nDevices = 0;
    for(address = 1; address < 127; address++ ){
        Wire.beginTransmission(address);
        error = Wire.endTransmission();
 
        if (error == 0){
            Serial.print("I2C device found at address 0x");
            if (address < 16)
                Serial.print("0");
            Serial.print(address,HEX);
            Serial.println(" !");
 
            nDevices++;
        }
        else if (error == 4) {
            Serial.print("Unknow error at address 0x");
            if (address < 16)
                Serial.print("0");
            Serial.println(address,HEX);
        } 
    }
    if (nDevices == 0)
        Serial.println("No I2C devices found\n");
    else
        Serial.println("done\n");
 
    delay(100);
   
}
}

void loop() {
  // put your main code here, to run repeatedly:
//float t = sht31.readTemperature();                // Считываем показания температуры  
//  float h = sht31.readHumidity();                   // Считываем показания влажности
 float t = aht20.readTemperature();
 float h = aht20.readHumidity();
    Serial.print("Temp *C = ");                     // Отправка текста 
    Serial.print(t);                                // Отправка температуры
    Serial.print("\t\t");                           // Отправка текста
    Serial.print("Hum. % = ");                      // Отправка текста
    Serial.println(h);                              // Отправка температуры
    float_0 = ads1015.readADC_Differential_0_1();
    Serial.print("ads = ");
    Serial.print(float_0 );
    delay(1000);                                    // Пауза 1 с
}
