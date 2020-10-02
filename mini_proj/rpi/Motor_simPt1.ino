#include "Arduino.h"

 #define inputCLK 2 //encoder clock pin
 #define inputDT 3 //encoder DT pin
#define motor 5

volatile byte aFlag = 0; // lets us know when we're expecting a rising edge on pinA to signal that the encoder has arrived at a detent
volatile byte bFlag = 0; // lets us know when we're expecting a rising edge on pinB to signal that the encoder has arrived at a detent (opposite direction to when aFlag is set)
volatile byte reading = 0; //somewhere to store the direct values we read from our interrupt pins before checking to see if we have moved a whole detent

 //encoder counts and variables
 double counter = 0; 

 //calculations 
 double Rev;
 double prevRev=0;
 double angularVelocity;
 double commandVoltage;
 double angularPosition;
 String angularVel;
 String commandVolt;
 String Revolutions;
 String anglePosition;
// Sampling time and display timing 
int current_time;
double sampleTime=0;
double samplePeriod=100;//10ms
int period =1000; //1 second

 //error stuff 
 bool doneRead =false;
 double errorTime = 0;
 int errorPeriod=10;
 //control
 //matlab

 void setup() 
 {    
   pinMode (inputCLK,INPUT_PULLUP);
   pinMode (inputDT,INPUT_PULLUP);
   pinMode(motor, OUTPUT);
   attachInterrupt(0, CLK, RISING);//using 2 interrupts for econder for most accurate positional results
   attachInterrupt(1, DT, RISING);
   Serial.begin (250000);  
  
 } 
 void loop() 
 { 
    doneRead=false;

       if(millis() >= sampleTime+samplePeriod)//gets the sampled values
   {
      Rev = counter/20; //Revolutions made in 100ms
      angularVelocity=((Rev-prevRev)*6.2832)/(samplePeriod/1000); // ([rev] * [rad/rev])/ ([ms]*[m])= rad/s
      commandVoltage=counter*12.75; // 1 cnt = 12.75 change in pwm so 1 rev is 20 cnts which means in 20 cnts the voltage is at its peak 255 duty cycle
      angularPosition= (Rev-prevRev)*360;
      prevRev=Rev;
      angularVel +=angularVelocity; //string to store velocity
      angularVel += ' '; //places space between values for cleaner look
      commandVolt+=commandVoltage; // string to store voltage
      commandVolt+=' '; //places space between values for cleaner look
      sampleTime += samplePeriod;
      Revolutions+=Rev; // string to store voltage
      Revolutions+=' '; //places space between values for cleaner look
      anglePosition+=angularPosition;
      anglePosition+=' '; //places space between values for cleaner look
    }
    if(millis() >= errorTime+errorPeriod && doneRead==true )
  {
   Serial.println("Error main too long");
   }
  if(millis() >= current_time+period) //each second this is ran
  {
    Serial.print("Time[ms]: ");
    Serial.println(millis());
    Serial.print("Angular Velocity: ");
    Serial.println(angularVel);
    Serial.print("Voltage: ");
    Serial.println(commandVolt);
    Serial.print("Revolution from start: ");
    Serial.println(Revolutions);    
    Serial.print("Relative angle position from previous spot: ");
    Serial.println(anglePosition);
    anglePosition = ""; //clears string
    angularVel = "";//clears string
    commandVolt = "";//clears string
    Revolutions ="";//clears string
    
    current_time += period; // resets the time for another second
  }
   errorTime += errorPeriod; // resets the error time
 }
 void CLK ()
 {
    cli(); //stop interrupts happening before we read pin values
  reading = PIND & 0xC; // read all eight pin values then strip away all but pinA and pinB's values
  if(reading == B00001100 && aFlag) { //check that we have both pins at detent (HIGH) and that we are expecting detent on this pin's rising edge
    counter --; //decrement the encoder's position count
    doneRead=true;
    if(counter <= 0){
      counter=0;
      }
    bFlag = 0; //reset flags for the next turn
    aFlag = 0; //reset flags for the next turn
 
  }
  else if (reading == B00000100) bFlag = 1; //signal that we're expecting pinB to signal the transition to detent from free rotation
  sei(); //restart interrupts
}
  void DT ()
  {
   cli(); //stop interrupts happening before we read pin values
  reading = PIND & 0xC; //read all eight pin values then strip away all but pinA and pinB's values
  if (reading == B00001100 && bFlag) { //check that we have both pins at detent (HIGH) and that we are expecting detent on this pin's rising edge
    counter ++; //increment the encoder's position count
    doneRead=true;
    if(counter >= 20){
      counter=20;
      }
    bFlag = 0; //reset flags for the next turn
    aFlag = 0; //reset flags for the next turn
  }
  else if (reading == B00001000) aFlag = 1; //signal that we're expecting pinA to signal the transition to detent from free rotation
  sei(); //restart interrupts
}
