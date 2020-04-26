#include <Wire.h>

// Relay controls solenoid that compresses AmBu bag
const unsigned int RelayPin       = 2;

// Switch that tells the program to not close the relay
const unsigned int SoftStopPin = 4;

// If we want a threshold for iniatiating inhaliation
unsigned int DefStartThold  = 0x8a14;

// I2C Address of the various sensors
const byte I2cAddrDlc = 41; //20" sensor
const byte I2cCmdDlc  = 0xAC; // CMD to request 2 cycle average (8ms)
const byte I2cAddrNpa = 40; //2" sensor
const byte I2CAddrScreen = 0x3C;  //Small display SSD1306 OLED

// Default parameters for AmBu squeazer
// Time between full breaths
unsigned long defRelayPeriod;
// Inhaliation Time Setting
unsigned long defRelayOnTime;

// Time to get a new measurmeent from the I2C sensors is ~8ms
unsigned long I2CPeriod;
unsigned long I2CLastReadTime;

// Arduino master time since boot
unsigned long currTime;

// Breath timing when was the relay opened
unsigned long relayOnMillis;

// When the last status string was sent
unsigned long prevStatusTime;

// Number of full breath cycles completed
unsigned int cycleCount;
// The return of the I2C sensors
unsigned int gaugePressure;
unsigned int flowPressure;

bool relayState; // is the relay open or closed?
bool runState; // Switch to turn off running

// Used in the functions that read the pressure sensors
byte i2cRaw[4];
byte i2cLow;
byte i2cHigh;

// Serail Buffer
char txBuffer[100];

void setup() {
   pinMode(RelayPin, OUTPUT);
   digitalWrite(RelayPin, LOW);
   relayState  = 0;
   runState = digitalRead(SoftStopPin);
   defRelayPeriod = 3000; //ms - default period for one breath
   defRelayOnTime = 1000; //ms - default inhalition time 
   I2CPeriod = 9; //ms
   cycleCount = 0;
   prevStatusTime = 0;
   relayOnMillis = 0;
   
   Serial.begin(57600);
   Wire.begin();
}

void loop() {
   currTime = millis();
   // Check if soft-off switch is on/off
   runState = digitalRead(SoftStopPin);

   if ((currTime - I2CLastReadTime) > I2CPeriod ) {
      gaugePressure = getGaugePressure();
      flowPressure = getFlowMeterPressure();
      // Every pressure readout send the relevent data to Plot (P)
      sprintf(txBuffer,"P %lu %u %u %u %u\n", 
                       currTime, cycleCount, relayState,
                       gaugePressure, flowPressure);
      Serial.write(txBuffer);
      I2CLastReadTime = currTime; 
   }
   // Once a second sent python the parameters being used for cycle times
   if ((currTime - prevStatusTime) > 1000 ) {
      sprintf(txBuffer,"S %lu %lu %lu\n", currTime, defRelayPeriod, defRelayOnTime);
      Serial.write(txBuffer);
      prevStatusTime = currTime;
   }

   // Is it time to turn off the relay
   if (relayState == true) {
      // The relay is ON, has it been on long enough?
      if ((currTime - relayOnMillis) >  defRelayOnTime) {
         // YES - Time to close the relay
         relayState = 0;
      }
   }

   // Is it time to initieate a new breath?
   if ((currTime - relayOnMillis) > defRelayPeriod ) {
      relayOnMillis = currTime;
      relayState = true;
      cycleCount++;
   }

   // Override relay, Assuming SS relay w/ ON=HIGH
   if ( runState == false ) {
      // the SoftStopPin says do not switch the relay on
      digitalWrite(RelayPin, LOW);
   }
   //Normal Mode
   else if ( runState == true ) {  
      if ( relayState == true ) {
         digitalWrite(RelayPin, HIGH);
      }
      else digitalWrite(RelayPin, LOW);
   }
}

// --ooo000OOO000ooo-- --ooo000OOO000ooo-- --ooo000OOO000ooo-- --ooo000OOO000ooo-- --ooo000OOO000ooo-- 
// --ooo000OOO000ooo-- --ooo000OOO000ooo-- --ooo000OOO000ooo-- --ooo000OOO000ooo-- --ooo000OOO000ooo-- 

unsigned int getGaugePressure() {
   // Read last cycles values for dlc 20" sensor
   /* The DLC returns 7 bytes: 
      0  : Status (we ignore this)
      1-3: Pressure [MSB, B1, LSB]
      4-6: Temp [MSB, B1, LSB] (not even requesting this)
   */
   // This sends stop after 4 bytes to release bus
   Wire.requestFrom(I2cAddrDlc, byte(4));
   for (int x=0; x < 4; x++) {
      i2cRaw[x] = Wire.read();
   }

   // Start new cycle for dlc 
   Wire.beginTransmission(I2cAddrDlc);
   Wire.write(I2cCmdDlc);
   Wire.endTransmission();

   gaugePressure = (i2cRaw[1] << 8) | i2cRaw[2];
   return (unsigned int) gaugePressure;
}

unsigned int getFlowMeterPressure() {
      // Read npa 2" sensor
      /*
      The NPA-700B-02WD can send pressure and temp data
      I guess the request for 2 bytes tells it only to sent pressure?
      The first byte returns 2 status bits, so & 00111111 removes them
      Why not convert to unsigned int now though?
      */
      Wire.requestFrom(I2cAddrNpa, byte(2));
      i2cHigh = Wire.read() & 0x3F;
      i2cLow = Wire.read();
      return (unsigned int) (i2cHigh << 8) | i2cLow;
}