
/* How to use the DHT-22 sensor with Arduino uno
   Temperature and humidity sensor
*/

//Libraries
#include <DHT.h>;
#include <Wire.h>
#define SLAVE_ADDRESS 0x08

//byte data_to_echo = 0;


//Constants
#define DHTPIN 7     // what pin we're connected to
#define DHTTYPE DHT22   // DHT 22  (AM2302)
DHT dht(DHTPIN, DHTTYPE); //// Initialize DHT sensor for normal 16mhz Arduino
#define VIRTUAL_CHANNEL 02


//Variables
int chk;
float hum;  //Stores humidity value
float temp; //Stores temperature value

void setup()
{
  Serial.begin(9600);
  Wire.begin(SLAVE_ADDRESS); //address 0x08
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);
  dht.begin();
}

void loop()
{
    
    delay(2000);
    //Read data and store it to variables hum and temp
    hum = dht.readHumidity();
    temp= dht.readTemperature();
    //Print temp and humidity values to serial monitor
    //Serial.print("Humidity: ");
    //Serial.print(hum);
    //Serial.print("%, ");
    Serial.print(temp);
    //Serial.print("°, ");
    //Serial.println(" Celsius");
    //Serial.println(" Data sent to master ");
    //Serial.print(data_to_echo);
    delay(10000); //Delay 2 sec.
}

// This function is called at intervals to send sensor data to Cayenne.
void receiveData(int bytecount)
{
  Serial.println(F("---> recieved events"));
  for (int i = 0; i < bytecount; i++) {
    temp = Wire.read();
  }
  Serial.print(bytecount);
  Serial.println(F("bytes recieved"));
  Serial.print(F("recieved value : "));
}

void sendData()
{
  Serial.println(F("---> recieved request"));
  Serial.print(F("sending value : "));
  
  
  Wire.write((char)temp);
  //Wire.write(char(hum))
;}
