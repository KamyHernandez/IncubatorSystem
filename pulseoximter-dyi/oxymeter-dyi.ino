#include <Wire.h>

int lect = A0;
int sign = 0;

#define SLAVE_ADDRESS 0x0b 
#define VIRTUAL_CHANNEL 01

//Variables
int chk;
float oxy_data;  //Stores humidity value

void setup() {
  Serial.begin(9600);
  pinMode(lect, INPUT);
  Wire.begin(SLAVE_ADDRESS);
  Wire.onRequest(sendData);
  //Wire.onReceive(receiveData);
  //Wire.onRequest(sendData);
  // put your setup code here, to run once:

}


void loop() {
  
  // put your main code here, to run repeatedly:
  sign = analogRead(lect);
  Serial.println(sign);
  if(sign >= 200)
  {
    digitalWrite(9,HIGH);
    }
  if(sign <= 199)
  {
    digitalWrite(9,LOW);
    }
  delay(300);
}

void sendData()
{
  Serial.println(F("---> recieved request"));
  Serial.print(F("sending value : "));
  
  
  Wire.write((byte)sign);
;}
