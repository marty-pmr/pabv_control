
#include "SensorDlcL20D4.h"
#include <Wire.h>
#include <Arduino.h>

#include <HardwareSerial.h>

SensorDlcL20D4::SensorDlcL20D4 () : GenericSensor(DLC_L20D4_ADDR) { }

void SensorDlcL20D4::setup() {

   // Start new cycle for dlc
   Wire.beginTransmission(addr_);
   Wire.write(DLC_L20D4_CMD); // 2 cycle average = 8ms
   Wire.endTransmission();
}

void SensorDlcL20D4::update(unsigned int ctime) {

   // Read last cycles values for dlc
   Wire.requestFrom(addr_, byte(4));
   for (x_=0; x_ < 4; x_++) data_[x_] = Wire.read();

   // Scaled value, upper 16 bits
   scaled_ = (data_[1] << 8) | data_[2];

   // Create serial representation
   sprintf(buffer_," 0x%.2x%.2x%.2x", data_[1], data_[2], data_[3]);

   // Start new cycle for dlc
   Wire.beginTransmission(addr_);
   Wire.write(DLC_L20D4_CMD); // 2 cycle average = 8ms
   Wire.endTransmission();
}

