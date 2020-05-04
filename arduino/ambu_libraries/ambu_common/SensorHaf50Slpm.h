
#ifndef __SENSOR_HAF50SLPM_H__
#define __SENSOR_HAF50SLPM_H__

#include "GenericSensor.h"

#define HAF_50SLPM_ADDR 73

class SensorHaf50Slpm : public GenericSensor {

   public:

      SensorHaf50Slpm ();

      void update(unsigned int ctime);

};

#endif
