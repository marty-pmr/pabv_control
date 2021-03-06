
#include "SensorHaf50Slpm.h"
#include <Wire.h>

#include <Arduino.h>

#include <HardwareSerial.h>

SensorHaf50Slpm::SensorHaf50Slpm () : GenericSensor(HAF_50SLPM_ADDR) { }


void SensorHaf50Slpm::update(unsigned int ctime) {

   // Read value
   Wire.requestFrom(addr_, byte(2));
   for (x_=0; x_ < 2; x_++) data_[x_] = Wire.read();

   // Scaled value
   scaled_ = (data_[0] << 8) | data_[1];

   // Create serial representation
   sprintf(buffer_," 0x%.2x%.2x", data_[0], data_[1]);

}


