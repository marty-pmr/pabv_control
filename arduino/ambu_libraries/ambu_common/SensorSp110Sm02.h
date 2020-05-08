
#ifndef __SENSOR_SP110SM02_H__
#define __SENSOR_SP110SM02_H__

#include "GenericSensor.h"

#define SP11_SM02_ADDR  0x28
#define SP11_SM02_INIT1 0b11001001
#define SP11_SM02_INIT2 0b11101001
#define SP11_SM02_DELAY 200

class SensorSp110Sm02 : public GenericSensor {

   public:

      SensorSp110Sm02 ();

      void setup();

      void update(unsigned int ctime);

};

#endif
