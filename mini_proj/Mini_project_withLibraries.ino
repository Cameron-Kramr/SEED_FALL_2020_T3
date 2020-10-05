/* Encoder Library - Basic Example
 * http://www.pjrc.com/teensy/td_libs_Encoder.html
 *
 * This example code is in the public domain.
 */

#include <Encoder.h>
const byte resetPin = 2;
long newPosition = 0;
bool interrupt = false;
double theta = 0;

// I think this comes from Rasberry PI
long oldPosition  = 0;


// Change these two numbers to the pins connected to your encoder.
//   Best Performance: both pins have interrupt capability
//   Good Performance: only the first pin has interrupt capability
//   Low Performance:  neither pin has interrupt capability
Encoder myEnc(3, 6);
//   avoid using pins with LEDs attached

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.println("Basic Encoder Test:");
  pinMode(resetPin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(resetPin), reset, CHANGE);
}

void loop() {
  // put your main code here, to run repeatedly:
  long newPosition = myEnc.read();
  if (newPosition != oldPosition) {
    oldPosition = newPosition;
    //Caclulating theta
    ////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////////////
    //THIS IS THE POSITION IN RADIANS
    theta = (double)newPosition*(double)2.0*(double)PI/(double)3600.0;
    ////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////////////
    Serial.print(newPosition);
    Serial.print("\t");
    //Serial.println(theta);
    Serial.println(digitalRead(resetPin));
  }

}



void reset(){
  myEnc.write(0);
}
