#include <ArduinoJson.h>
#include "Constant.h"                    /*header con enum e costanti*/
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <DHT.h>

#define DHTTYPE DHT11
#define DHTPin D1                       /*usare le GPIO 4 e 5 che sono D2 e D1*/

#define AMOISTUREPin A0

#define SLEEPING_TIME 1*(6e7)          /* 6e7 è un minuto*/

DHT dht(DHTPin, DHTTYPE);

WiFiUDP Udp;

char InputDG[4];                         /*vettore di char per contenere il payload del Datagram in ingressi*/
char _REPLYJSON[200];                    /*vettore di char per scrivere il contenuto JSON da inviare*/

float temperatura;                       /*variabili per il sensore DHT11*/
float umidita;
float terra;


StaticJsonDocument<200> doc;             /*JSON documento -> Static alloca nello stack*/


void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);      /*nel mio nesp8266 (nodemcu by amica) high abbassa il led_builtin*/

  Serial.begin(_BAUD);
  Serial.println("Connessione all'hardware...");

  pinMode(DHTPin, INPUT);               /*setup sensore umidità e temperatura*/
  dht.begin();   

  WiFi.begin(_SSID, _PASSWORD);         /*connessione alla rete WiFi locale*/
  Serial.printf("Tentativo di connessione a %s ...\n", _SSID);
  int i = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(++i); Serial.print(' ');
  }

  Serial.println('\n');
  Serial.println("Connessione stabilita!");  
  Serial.printf("Indirizzo IP:\t %s\n", WiFi.localIP().toString().c_str());

  Udp.begin(_UDPPORT);                  /*Creazione SOCKET di tipo DATAGRAM*/
  Serial.printf("In ascolto su %s:%d\n", WiFi.localIP().toString().c_str(), _UDPPORT);
}




void loop() {
  memset(_REPLYJSON,0,strlen(_REPLYJSON));           /*string reset*/

  temperatura = dht.readTemperature();
  umidita = dht.readHumidity();
  terra = analogRead(AMOISTUREPin);
  
  Serial.printf("temperature: %f\n", temperatura);
  Serial.printf("air-humidity: %f\n", umidita);
  Serial.printf("soil-humidity: %f\ns", terra);
  doc["plant"] = "Nagamorich";
  doc["temperature"] = temperatura;
  doc["air-humidity"] = umidita;
  doc["soil-humidity"] = terra;
  serializeJson(doc, _REPLYJSON);
  Udp.beginPacket(_IPADDR, _UDPPORT);
  Udp.write(_REPLYJSON);
  Udp.endPacket();
  delay(1000);
  Serial.flush();
  ESP.deepSleep(SLEEPING_TIME);
  //delay(10000);
}
