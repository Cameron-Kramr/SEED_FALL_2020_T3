//Arduino code used to control the velocity of each wheel with inputs of radius desired angular velocity and desired linear velocity
#include <Encoder.h>
#include "DualMC33926MotorShield.h" //PWm goes from -400 to 400 
#include <AutoPID.h>

//Pin setup
#define nD2 4 //tri-state disables both outputs of both motor channels when low
#define M1Dir 7 // Motor 1 direction input (voltage sign M1)
#define M2Dir 8 // motor 2 direction input (Voltage sign M2)
#define M1PWM 9 // Motor 1 speed input (Command Voltage M1)
#define M2PWM 10 // Motor 2 speed input (command Votlage M2)
#define nSF 12 //Status flag


#define kp_A (46.2979731521748)     //Wheel 2 velocity por. gain
#define kd_A (0)  //Wheel 2 velocity dif. gain
#define ki_A (461.590792327183)   //Wheel 2 velocity int. gain

#define kp_B (46.6050777553275)   //Wheel 2 velocity por. gain
#define kd_B (0) //Wheel 2 velocity dif. gain
#define ki_B (515.918210751475)   //Wheel 2 velocity int. gain

Encoder MotorEncoder1(2,6); //used 2 and 3 as they have the best interrupt timing, will need to change when adding second motor
Encoder MotorEncoder2(3,5); //used 2 and 3 as they have the best interrupt timing, will need to change when adding second motor
//comm stuff
int index = 0;
char space[1] = {' '};                                    //needed so the program knows to split up input string whenever a space occurs
char stringInput[30];                                     //the char array that the input string is placed in
String tooken[5];                                         //5 commands per string sent
float RFloat;                                             //dummy global variables
float OFloat;
float TFloat;
float VFloat;

double counter1=0; //counter for motor 1 and 2 resp.
double counter2=0;
double counter1_offset=0;
double counter2_offset=0;

double RadA=0;//current radial position sampled 
double RadB=0;

double Vel_A=0; // Radial Velocity of motor 1
double Vel_B=0; // Radial Velocity of motor 2

double Vel_WA=0;
double Vel_WB=0;

double Vel_L=0;
double Vel_S=0;

double RadAPrev=0;//Previous radial positon of wheel 1 before being sampled again
double RadBPrev=0;

double output_A=0;//PWM output for wheel 1
double output_B=0;//PWM output for wheel 2

double setpoint_A=0; //Wanted wheel 1 velocity
double setpoint_B=0; //Wanted wheel 2 velocity

//User-defined parameters needed for the operation 
double Radius=0; //Radius of circle 
double omega=0; //anglular velocity desired
double inputVel=0; //linear velocity desired

//Robot defined parameters
double r=2.88/12;// Radius of wheel in feet
double d=(13.15/2)/12; //Distance wheel to center in feet

//Timing stuff
double Time_1=0; // time delay for next interval
double Interval_time=5;//sample interval time =5ms
double Time=0;
double TimeSpin=0;
double TimeDes=0;


//function stuff
double Vel=0;
double count1=0;
double count2=0;
double rev=0;
double Rad=0;
bool Hit_Hard_Code=false;
int i=0;
//Initialize PID class variables

AutoPID Vel_A_PID(&Vel_A,&setpoint_A,&output_A,-300,300,kp_A,ki_A,kd_A);
AutoPID Vel_B_PID(&Vel_B,&setpoint_B,&output_B,-300,300,kp_B,ki_B,kd_B);

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
   Serial.begin (1000000);//baud rate set to 250000
   Vel_A_PID.setTimeStep(Interval_time);
   Vel_B_PID.setTimeStep(Interval_time);
}

//convert motor counts into radial position of each wheel
void CountsToRad(double count1,double count2,double* RadA, double* RadB)
{
   rev=(count1)/(64*50); // Get revolutions made for the motor 
   *RadA=rev*6.2832; // Get radians made for the motor 
   rev=(count2)/(64*50); // Get revolutions made for the motor 
   *RadB=rev*6.2832; // Get radians made for the motor 
}
//converts radial position of each wheel into linear velocity of each wheel 
void RadToVel (double RadA,double RadB, double RadAPrev, double RadBPrev, double Interval_time, double* Vel_A, double* Vel_B)
{
  *Vel_A=((RadA-RadAPrev)/(Interval_time/1000))*(2.88/12);
  *Vel_B=((RadB-RadBPrev)/(Interval_time/1000))*(2.88/12);
}

//finds setpoint of linear velocity with a given angular velocity
void AngularVelToLinearA(double omega,double Radius, double* Vel_WA, double* Vel_WB)
{
     if(Radius>0)
   {
    *Vel_WA=omega*(Radius+d);//relook at d I dont remeber but i think the 1/2 needs to be removed for this equation to hold
    *Vel_WB=omega*(Radius-d);  
    }
    else{
    *Vel_WA=omega*(Radius-d);
    *Vel_WB=omega*(Radius+d);
      }

}

//sums the linear input velocity and the linear velocity derived from the angular velocity
double SummingBlock(double Vel_W,double inputVel)
{
   Vel_S=Vel_W+inputVel;
   return Vel_S;
}


void HardCodeSpin(double *omega, double *Radius,double Timespin,double Time_1)
{
  if(Time_1>=TimeSpin){//spin 90 deg
  *omega=1.5;
  *Radius=0;
  }
  if(Time_1>=TimeSpin+1300)//reach 90 degs and stop
  {
  *omega=0;
  *Radius=0;
  }
   if(Time_1>=TimeSpin+1300+500)//wait .5 seconds after stopping to move around the beacon with a radius of 1
  {
  *omega=1.25;
  *Radius=1;
  }
   if(Time_1>=TimeSpin+1300+500+5590)//finish the movement around the beacon set all values back to zero
  {
  *omega=0;
  *Radius=0;
  }
}

void decodeString(){
  if (Serial.available() > 0){
    Serial.readBytesUntil('@',stringInput,30);                      //the "@" is arbitrary, only reads in 30 characters
    tooken[index] = strtok(stringInput, space);                     //this splits off a chunk of the input string (until the first ' ') and puts it in a string array
    counter1_offset = MotorEncoder1.read();
    counter2_offset = MotorEncoder2.read();
    RadAPrev = 0;
    RadBPrev = 0;
    Time=0;
    switch (tooken[index][0]){                                      //chooses which variable to set based on first character of the current string
        case 'R':
          tooken[index].setCharAt(0,'0');                           //sets the first character to a zero so only the float is left
          RFloat = tooken[index].toFloat();                         //sets corresponding global variable to the float determined
          Radius=double(RFloat);
          break;

        case 'O':
          tooken[index].setCharAt(0,'0');                          //sets the first character to a zero so only the float is left
          OFloat = tooken[index].toFloat();                         //sets corresponding global variable to the float determined
          omega=double(OFloat);
          break;
        
        case 'T':
          tooken[index].setCharAt(0,'0');                          //sets the first character to a zero so only the float is left
          TFloat = tooken[index].toFloat();                         //sets corresponding global variable to the float determined
          TimeDes=double(TFloat)*1000+550;                         //*1000+550, because comes in in seconds and the 550 is for the rise time delay
          break;
        
        case 'V':
          tooken[index].setCharAt(0,'0');                         //sets the first character to a zero so only the float is left
          VFloat = tooken[index].toFloat();                       //sets corresponding global variable to the float determined
          inputVel=double(VFloat);
          break;
        
        case 'C':
          Hit_Hard_Code=true;                                     //Bool statement to set true when we reach the special case C
          i=0;                                                    //reset i=0 so we can go back through the hard code if so pleased 
          break;
          
        default:
          break;
    }

    while (index < 5){                                                //This will loop the same things as above, but for each other commands in the input string
      if (tooken[index] != NULL){                                     //checks if there are more command strings left
        index++;
        tooken[index] = strtok(NULL,space);                           //splits off another chunk of the input string (another command)
        
        switch (tooken[index][0]){
          case 'R':
            tooken[index].setCharAt(0,'0');                          //sets the first character to a zero so only the float is left
            RFloat = tooken[index].toFloat();                         //sets corresponding global variable to the float determined
            Radius=double(RFloat);
            break;

          case 'O':
            tooken[index].setCharAt(0,'0');                          //sets the first character to a zero so only the float is left
            OFloat = tooken[index].toFloat();                        //sets corresponding global variable to the float determined
            omega=double(OFloat);
            break;
        
          case 'T':
            tooken[index].setCharAt(0,'0');                          //sets the first character to a zero so only the float is leftleft
            TFloat = tooken[index].toFloat();                        //sets corresponding global variable to the float determined
            TimeDes=double(TFloat)*1000+550;                         //*1000+550, because comes in in seconds and the 550 is for the rise time delay
            break;
        
          case 'V':
            tooken[index].setCharAt(0,'0');                          //sets the first character to a zero so only the float is left
            VFloat = tooken[index].toFloat();                        //sets corresponding global variable to the float determined
            inputVel=double(VFloat);                        
            break;
        
          case 'C':
            Hit_Hard_Code=true;                         
            i=0;
            break;
          
          default:
               break;  
        }
      }
      
      else {
        //Serial.println(index);
        index = 5;                                                    //breaks out of the while loop
        //Serial.println("It was NULL.");
      }
    }
    
    index = 0;
    while (index<5){                                                        //clears the tookens that hold each string inputed
      tooken[index] = "";
      index++;
    }
    
    index = 0;
    for (int i=0; i<30; i++){                                               //clears the stringInput array
      stringInput[i] = 0;
    }
  }
}
void loop() {
  while(millis()> Time_1 + Interval_time)
  {
      if(Time>=TimeDes)
      {
        omega=0;
        Radius=0;
        inputVel=0;
 
        }
     decodeString(); //Decodes values sent from the serial 
    
       if(Hit_Hard_Code == true && i==0)//WHen we reach the special character start the spin
      {
      TimeSpin=Time_1; //set the spin time as the current sample time
      HardCodeSpin(&omega,&Radius,TimeSpin,Time_1);    //run the spin function
      i++;//increment so the time doesnt get reset to the current sample time
      }
      if(Hit_Hard_Code ==true && i!=0)//used so the hardcode spin could be continually ran 
      {
        HardCodeSpin(&omega,&Radius,TimeSpin,Time_1);
      }

     counter1=-1*MotorEncoder1.read()-(-1*counter1_offset); //get motor counts for motor 1 multiplied by -1 because the counts were backwards
     counter2=MotorEncoder2.read()-counter2_offset;  //get motor counts for motor 2
     
     //finiding radial positon of each wheel 
     CountsToRad(counter1,counter2,&RadA,&RadB);
  
     // Finding linear velocity from the radial position of each wheel 
      RadToVel(RadA,RadB,RadAPrev,RadBPrev,Interval_time,&Vel_A,&Vel_B);
  
     //Angular velocity input converted to linear velocity of each wheel
     AngularVelToLinearA(omega,Radius,&Vel_WA,&Vel_WB);
     
     //Summing block to set setpoint for wheel velocity control   
     setpoint_A=SummingBlock(Vel_WA,inputVel);
     setpoint_B=SummingBlock(Vel_WB,inputVel);
  
     //runs the velocity controllers 
     Vel_A_PID.run(); 
     Vel_B_PID.run();

    //sets the output of the controllers (PWM) to run the motors
     motor_shield.setM1Speed(output_A);
     motor_shield.setM2Speed(output_B);
    
     RadAPrev=RadA;
     RadBPrev=RadB;
  
     Time_1+=Interval_time; //Change time so it runs at an incremeted 10ms
     Time+=Interval_time;
    }

}
