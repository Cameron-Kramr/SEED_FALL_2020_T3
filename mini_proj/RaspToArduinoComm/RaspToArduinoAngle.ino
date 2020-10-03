#include <Wire.h>
#define Sl_Addrs 0x08                                 //this address and the address in raspberry PI code should be the same,
 int nnumber = 0;                                     //but it does not have to be 0x08
 int bep = 0;
 int degree;
 float rads;
 float oldRads = 3.14159;                             //placeholder value for old position in rads
 int oldDegree;
 bool conv = false;
 
void setup() {
  Serial.begin(9600);
  Wire.begin(Sl_Addrs);
  Wire.onReceive(changeNum);
  Wire.onRequest(seBack);
}

void changeNum(int byteC){                            //reads data recieved from raspberry PI
  bep = Wire.read();
  bep = bep + Wire.read();
  nnumber = nnumber + bep;                            //puts data in variable nnumber
}

void seBack(){
  conv = true;                                        //lets the loop() convert recieved data to rads
  oldDegree = round((oldRads/0.01745329251)*0.7);     //converts oldRads to a number between 0 - 252 in order to send data easier
  //Serial.println(oldDegree);
  Wire.write(oldDegree);                              //sends old wheel position to raspberry PI
}

void loop() {
  if (conv == true){
    degree = round (nnumber / 0.7);                   //converts data recieved to degrees
    rads = degree * 0.01745329251;                    //converts degrees to rads
    //Serial.println(degree);
    //Serial.println(rads);
    conv = false;
    nnumber = 0;
    bep = 0;
  }
  delay(100);
}
