#include <ArduinoJson.h>
#include <LiquidCrystal.h>
#include "dht.h"

dht DHT;

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);
const int ledPinGreen = 8;  
const int ledPinRed = 9; 
const int ledPinYellow = 10; 
const int pinoDHT11 = A2;
String texts[] = {"Asmongold:", "Cybercryx:", "Temperature:"};
int asmongold = false;
int wow = false;
int chatmode = 1;
String message = "loading...";

void setup() {  
  Serial.begin(9600); 
  lcd.begin(16, 2);
  pinMode(ledPinGreen, OUTPUT); 
  pinMode(ledPinRed, OUTPUT);
  pinMode(ledPinYellow, OUTPUT); 
  pinMode(13, INPUT_PULLUP);    
  delay(2000);
}

void displayLcd(){
  if(chatmode == 1){
    digitalWrite(ledPinYellow, HIGH);
    lcd.clear();
    lcd.setCursor(0, 1);
    lcd.print(message);
  }else{
    DHT.read11(pinoDHT11);
    for (int i = 0; i < sizeof(texts) / sizeof(texts[0]); i++) {
    
      lcd.clear();
      lcd.setCursor(0, 1);
      lcd.print(texts[i]);

      if(texts[i] == "Asmongold:"){
        lcd.setCursor(11, 1);
        lcd.print(asmongold ? "LIVE" : "OFF");
      }else if(texts[i] == "Cybercryx:"){
        lcd.setCursor(11, 1);
        lcd.print(wow ? "ON" : "OFF");
      }else if(texts[i] == "Temperature:"){
        lcd.setCursor(13, 1);
        lcd.print(DHT.temperature, 0);
      }
      delay(2000);
    }
  }
}

void pythonInfo(){
    if (Serial.available() > 0) {  
    String infoSerial = Serial.readStringUntil('\n');  

    DynamicJsonDocument doc(1024); 
    DeserializationError error = deserializeJson(doc, infoSerial);

   if (error) {
      Serial.print("Error: ");
      Serial.println(error.c_str());
      return;
    }

    asmongold = doc["asmongold"];
    wow = doc["wow"];
    message = doc["message"].as<String>();
    
    if (asmongold == true) {
      digitalWrite(ledPinGreen, HIGH);
    } else {
      digitalWrite(ledPinGreen, LOW);
    }
    
    if(wow == true){
      digitalWrite(ledPinRed, HIGH);
    } else {
      digitalWrite(ledPinRed, LOW);
    }

  }
}

void loop() {

   pythonInfo();
  
  if (digitalRead(13) == LOW) { 
    if(chatmode == 1){
      chatmode = 0;
      digitalWrite(ledPinYellow, LOW);
    }else{
      chatmode = 1;
    }

  }

  displayLcd();
  delay(1000);
}