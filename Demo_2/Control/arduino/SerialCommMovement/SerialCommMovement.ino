//moving the system a dedicated amount of feet (still needs to be tested).
#include <Encoder.h>
#include "DualMC33926MotorShield.h" //PWm goes from -400 to 400 
#include <AutoPID.h>

//COMMS
#define COMMS_BUFFER 64

//Pin setup
#define nD2 4 //tri-state disables both outputs of both motor channels when low
#define M1Dir 7 // Motor 1 direction input (voltage sign M1)
#define M2Dir 8 // motor 2 direction input (Voltage sign M2)
#define M1PWM 9 // Motor 1 speed input (Command Voltage M1)
#define M2PWM 10 // Motor 2 speed input (command Votlage M2)
#define nSF 12 //Status flag

// Control variables
#define kp_P (4)//Positional por. gain
#define kd_P (100)//Positional dif. gain
#define ki_P (0)//Positional int. gain

#define kp_A (50)     //Wheel 2 velocity por. gain
#define kd_A (100)  //Wheel 2 velocity dif. gain
#define ki_A (100)   //Wheel 2 velocity int. gain

#define kp_B (50)   //Wheel 2 velocity por. gain
#define kd_B (100)  //Wheel 2 velocity dif. gain
#define ki_B (100)   //Wheel 2 velocity int. gain


//COMMS Variables:
byte comm_buffer[COMMS_BUFFER];
String Test_MSG;

Encoder MotorEncoder1(2,5); //used 2 and 3 as they have the best interrupt timing, will need to change when adding second motor
Encoder MotorEncoder2(3,6); //used 2 and 3 as they have the best interrupt timing, will need to change when adding second motor

double counter1=0; //counter for motor 1 and 2 resp.
double counter2=0;

double counter1_offset=0; //counter for motor 1 and 2 resp.
double counter2_offset=0;

double rev1=0;
double rev2=0;// revolutions made for motor 1 and 2 resp.

double Rad1=0;
double Rad2=0;

double Vel_A=0; // Radial Velocity of motor 1
double Vel_B=0; // Radial Velocity of motor 2

double Rad1Prev=0;
double Rad2Prev=0;

double Position_RA=0;//Current distance traveled calculated
double Position_RB=0;//Current distance traveled calculated


double output_A=0;
double output_B=0;
double output_RA=0;
double output_RB=0;

double setpoint_A=0; //Wanted wheel 1 velocity
double setpoint_B=0; //Wanted wheel 2 velocity
double setpoint_RA=0; // distance to be traveled in feet
double setpoint_RB=0;

double r=2.88/12;// Radius of wheel in feet
double Radius=0; //Radius of circle 
double d=(13.125/2)/12; //Distance wheel to center in feet
double omega=0; //angle {Rad}
//double Des_time=(pow((.403/des_Rad),-1)*1000);

double Time_1=0; // time delay for next interval
double Interval_time=5;//sample interval time =5ms

//Initialize PID class variables
AutoPID Vel_A_PID(&Vel_A,&setpoint_A,&output_A,-400,400,kp_A,ki_A,kd_A);
AutoPID Vel_B_PID(&Vel_B,&setpoint_B,&output_B,-400,400,kp_B,ki_B,kd_B);

AutoPID RotationalPositionA_PID(&Position_RA,&setpoint_RA,&output_RA,-10,10,kp_P,ki_P,kd_P);
AutoPID RotationalPositionB_PID(&Position_RB,&setpoint_RB,&output_RB,-10,10,kp_P,ki_P,kd_P);

//AutoPID myPID(&Position,&setpoint_B,&output_B,-400,400,kp,ki,kd);

DualMC33926MotorShield motor_shield;

void setup() {
  // put your setup code here, to run once:
   pinMode(nD2,OUTPUT); 
   pinMode(M1Dir,OUTPUT);
   pinMode(M2Dir,OUTPUT);
   pinMode(M1PWM,OUTPUT);
   pinMode(M1PWM,OUTPUT);
   pinMode(nSF,INPUT);     
   motor_shield.init(); 
   Serial.begin (250000);//baud rate set to 250000
   Vel_A_PID.setTimeStep(Interval_time);
   Vel_B_PID.setTimeStep(Interval_time);
   RotationalPositionA_PID.setTimeStep(Interval_time);
   RotationalPositionB_PID.setTimeStep(Interval_time);

}

//Convert serial data in char array to radius and theta values
void convert_Serial_Data(double *radius, double *theta, char *data){
  static char delims[] = " \t\n";
  String message;
  message = strtok(data, delims);
  (*radius) = message.toFloat();
  message = strtok(NULL, delims);  
  (*theta)  = message.toFloat();
}

void loop() {

while(millis()> Time_1 + Interval_time)
{

  if (Serial.available() > 0){                          //checks if bytes were sent
    Serial.readBytesUntil('\n',comm_buffer,COMMS_BUFFER);                  //reads in all the bytes
    convert_Serial_Data(&Radius, &omega, comm_buffer);
    
    sprintf(comm_buffer, "Radius: %d\n\r", Radius);
    Test_MSG = comm_buffer;
    Serial.println(Radius);
    sprintf(comm_buffer, "Omega: %d\n\r", omega);
    Test_MSG = comm_buffer;
    Serial.println(omega);
    Serial.println("ACK");
    
    counter1_offset = MotorEncoder1.read();
    counter2_offset = MotorEncoder2.read();

    Rad1Prev = 0;
    Rad2Prev = 0;
  }

  //Grab motor encoder counts
   counter1=MotorEncoder1.read() - counter1_offset; //get motor counts for motor 1
   counter2=MotorEncoder2.read() - counter2_offset;  //get motor counts for motor 2

   //Convert encoder counts to rotations
   rev1=(counter1)/(64*50); // Get revolutions made for motor 1
   rev2=(counter2)/(64*50); // Get revolutions made for motor 2

   //Convert motor rotations to radians
   Rad1=rev1*6.2832; // Get radians for motor 1
   Rad2=rev2*6.2832; // Get radians for motor 2 

    //Calculate radial velocity of each wheel
   Vel_A=(Rad1-Rad1Prev)/(Interval_time/1000); //{Rad/s}
   Vel_B=(Rad2-Rad2Prev)/(Interval_time/1000); //{Rad/s}

    //Determine linear distance each wheel travels
   Position_RA=2*3.14*r*rev1;
   Position_RB=2*3.14*r*rev2;

    //Calculate setpoints for linear distance of each wheel
    if(omega != 0){
     setpoint_RA=(omega*(Radius+d));
     setpoint_RB=(omega*(Radius-d));  
    }else{
      setpoint_RA=(Radius);
      setpoint_RB=(Radius);
    }

   //Run Rotational position PID
   RotationalPositionA_PID.run();
   RotationalPositionB_PID.run();

  //Get new velocity setpoints  
   setpoint_B=(output_RB); // Get current linear velocity for motor 2 {Rad/s}
   setpoint_A=(output_RA); // Get current linear velocity for motor 1 {Rad/s}

  //Update velocity PID
   Vel_A_PID.run(); 
   Vel_B_PID.run();

  //Push control values to motor output
   motor_shield.setM1Speed(output_A);
   motor_shield.setM2Speed(output_B);
   /*
   Serial.print(Position_RA);
   Serial.print('\t');
   Serial.print(setpoint_RA);
   Serial.print('\t');
   Serial.print(Position_RB);
   Serial.print('\t');
   Serial.print(setpoint_RB);
   Serial.println('\t');
   /*
   Serial.print(Vel_A);
   Serial.print('\t');
   Serial.print(setpoint_A);
   Serial.print('\t');
   Serial.print(Vel_B);
   Serial.print('\t');
   Serial.print(setpoint_B);
   Serial.print('\t');
   Serial.print(Radius);
   Serial.print('\t');
   Serial.print(omega);
   Serial.print('\n');
   */
   Rad1Prev=Rad1;
   Rad2Prev=Rad2;

   Time_1+=Interval_time; //Change time so it runs at an incremeted 10ms
  }

}
