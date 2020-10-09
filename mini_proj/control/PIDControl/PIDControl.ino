//changes the position of the motor by 1 rad at a specified time (this one should be adapted to work with our motor, still need to check) 
#include <Encoder.h>
#include <AutoPID.h>
#include "DualMC33926MotorShield.h"
#include <Wire.h>
#include <math.h>

DualMC33926MotorShield md;
//pin defenitions
#define nD2 4 //tri-state disables both outputs of both motor channels when low
#define M1Dir 7 // Motor 1 direction input (voltage sign M1)
#define M2Dir 8 // motor 2 direction input (Voltage sign M2)
#define M1PWM 9 // Motor 1 speed input (Command Voltage M1)
#define M2PWM 10 // Motor 2 speed input (command Votlage M2)
#define nSF 12 //Status flag
Encoder MotorEncoder(2,5); //used 2 and 3 as they have the best interrupt timing, will need to change when adding second motor

//calculation variables
double counter=0;
String Revolutions;
double rev;
double prevRev=0;
double commandVoltage=255;
double Rad=0;
String WheelPosition;//in rad
String CurrentTime;

// Sampling time and display timing 
double current_time=0;//time used un the 1 second display and start of the motor
double sampleTime=0;
double samplePeriod=10;//50ms
double DedicatedTime =3000; //time in ms set to change from inital 0 rad to 1 rad, saying at 3 seconds the motor will begin to move to the postion
int i=0;
bool TimeMade=false;// bool to check and see that the allocated time has reached where we want it to be
int x=0; 
bool lessThan = false;
//control 
#define kp (300)// [PWM/rad]
#define kd 0// v/angularVelocity [PWM/rad/s]
#define ki (30)// PWM*rad*s
#define Sl_Addrs 0x08 

double output;// this is the voltage(PWM) output
double setpoint=0;// this is the point we want in rads 


AutoPID myPID(&Rad,&setpoint,&output,-400,400,kp,ki,kd);

void setup() {
  // put your setup code here, to run once:
   pinMode(nD2,OUTPUT); 
   pinMode(M1Dir,OUTPUT);
   pinMode(M2Dir,OUTPUT);
   pinMode(M1PWM,OUTPUT);
   pinMode(M1PWM,OUTPUT);
   pinMode(nSF,INPUT);      
   Serial.begin (250000);//baud rate set to 250000
   md.init();
   myPID.setTimeStep(111);// time interval found from plot was sigma=90ms
   Wire.begin(Sl_Addrs);
   Wire.onReceive(Receive_Handler);
   Wire.onRequest(Send_Handler);
}

void Receive_Handler(char cbyte){
  int16_t bytes = 0;
  static int8_t datum = 0;
  static int8_t value = 0;

  bytes = Wire.available();
  //Serial.print("Reading Data. Bytes: ");
  //Serial.println(bytes);

  //When set point commands are sent, two bytes are received, but only the second one is useful.
  if(bytes == 2){
    datum = Wire.read();
    datum = Wire.read();
    setpoint = datum*M_PI/128;
    Serial.println(setpoint);
  }
  else{
    //Serial.println("No Useful Data");
    for(uint8_t i = 0; i < bytes; i ++)
      Wire.read();
  }
  }

void Send_Handler(){
  int8_t data_out = Rad*128/M_PI;
  Wire.write(data_out);
  Serial.println("Sending Data");
  //Serial.println(data_out);
}

void loop() {
  // put your main code here, to run repeatedly:

if(millis() >= current_time+samplePeriod)//gets value of the position every sampled time
{
  counter=MotorEncoder.read(); //counts current position
  rev=counter/(64*50); // its divided by 64*50 [counts per gear ratio] as thats how many counts are in 1 revolution (540 for my motor im testing)
  //Serial.println(counter);
  current_time+=samplePeriod;
  Rad=(rev*6.2832); // rev converted to rad
  myPID.run();
  
  md.setM1Speed(output);
  //Serial.print(Rad);
  //Serial.print("\t");
  //Serial.println(output);
  }

}
